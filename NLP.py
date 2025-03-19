from transformers import pipeline, AutoTokenizer
import sqlite3
import json
import re
from camel_tools.ner import NERecognizer
from camel_tools.tokenizers.word import simple_word_tokenize
import time
from langdetect import detect

class belaNER():
    
    def __init__(self):
        # Arabic NER pipeline
        self.tokenizer_ar = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")
        self.max_length = self.tokenizer_ar.model_max_length  # commonly 512 for BERT-based models
        self.chunk_size = self.max_length - 2  # reserve space for [CLS] and [SEP]
        self.ner_ar = pipeline('ner', model='CAMeL-Lab/bert-base-arabic-camelbert-mix-ner', aggregation_strategy="none")
        
        # English NER pipeline
        self.ner_en = pipeline('ner', model='Davlan/distilbert-base-multilingual-cased-ner-hrl', aggregation_strategy="none")
        

    def language_detection(self, sentence):
        if len(sentence) == 0:
            return None
        else: 
            try:
                language = detect(sentence)
                return language
            except:
                return None

    def clean(self, sentence):
        """Cleans text by removing special characters, HTML, URLs, and emojis."""
        sentence = re.sub(r'http\S+', ' ', sentence)  # Remove URLs
        sentence = re.sub(r'<.*?>', ' ', sentence)  # Remove HTML tags
        sentence = sentence.replace("#", "").replace("@", "").replace("\t", " ").replace("\r", " ").replace("\n", " ")
        return re.sub(r'\s+', ' ', sentence).strip()  # Remove extra spaces
    
    def chunk(self, text):
        # Tokenize the provided text
        tokens = self.tokenizer_ar.tokenize(text)
        # Create token chunks of size 'chunk_size'
        token_chunks = [tokens[i:i+self.chunk_size] for i in range(0, len(tokens), self.chunk_size)]
        # Convert token chunks back to text
        text_chunks = [self.tokenizer_ar.convert_tokens_to_string(chunk) for chunk in token_chunks]
        return text_chunks
    
    def extract_entities(self, text, language='ar'):
        # Chunk the text to ensure no input exceeds the token limit
        if language == 'ar':
            chunks = self.chunk(text)
            all_entities = []
            # Process each chunk separately with the NER pipeline
            for chunk in chunks:
                entities = self.ner_ar(chunk)
                for entity in entities:
                    # Round the score for clarity
                    entity['score'] = round(float(entity['score']), 2)
                all_entities.extend(entities)
        else:
            entities = self.ner_en(text)
            for entity in entities:
                # Round the score for clarity
                entity['score'] = round(float(entity['score']), 2)
            all_entities = entities
        return self.merge_entities(all_entities)
    
    def merge_entities(self, entities):
        if not entities:
            return []
        merged_entities = []
        for entity in entities:
            # If the token starts with "##", merge with the previous entity if available
            entity['score'] = round(float(entity['score']), 2)
            # if the entity starts with B- or I- then it is a part of a multi-word entity
            if entity['entity'][0] == 'B' and not "##" in entity['word']:
                merged_entities.append(entity)
            elif entity['entity'][0] == 'I' or "##" in entity['word']:
                if len(merged_entities) > 0:
                    if "##" in entity['word']:
                        merged_entities[-1]['word'] += str(entity['word']).replace("##", "")
                    else:
                        merged_entities[-1]['word'] += " " + entity['word']
            else:
                merged_entities.append(entity)  
        return merged_entities

 
def extract_entities():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()


    # Retrieve the 10 most recent entries (assuming 'id' represents the order)
    cursor.execute("SELECT id, title, summary FROM entries WHERE entities IS NULL ORDER BY published DESC")
    rows = cursor.fetchall()

    ner_extractor = belaNER()

    print("There are {} entries that need entity extraction".format(str(len(rows))))

    # Process each entry to extract entities and update the database
    for i in range(len(rows)):
        # wait a second 
        if i % 10 == 0:
            time.sleep(3)
        if i % 100 == 0:
            time.sleep(10)
        
        print("Processing entry", i)
        row = rows[i]
        
        entry_id, title, summary = row
        
        # set the language of the sentence
        title = ner_extractor.clean(title)
        summary = ner_extractor.clean(summary)
        
        language = ner_extractor.language_detection(title)
        cursor.execute("UPDATE entries SET language = ? WHERE id = ?", (language, entry_id))
        
        
        print(title, language)
        
        entities = []
        locations = []
        organizations = []
        persons = []
        
        if language == 'ar':
            print("Extracting entities from the sentence:", title)
            entities = ner_extractor.extract_entities(title, language='ar') 
            print("Entities:", entities)
        else:
            print("Extracting entities from the sentence:", title)
            entities = ner_extractor.extract_entities(title, language='en')
            print("Entities:", entities)

        if entities:
            locations = [entity['word'] for entity in entities if 'LOC' in entity['entity']]
            organizations = [entity['word'] for entity in entities if 'ORG' in entity['entity']]
            persons = [entity['word'] for entity in entities if 'PER' in entity['entity']]
            
        cursor.execute("""
            UPDATE entries 
            SET entities = ?, 
                LOC = ?, 
                ORG = ?, 
                PER = ?,
                language = ?
            WHERE id = ?
        """, (json.dumps(entities), 
            json.dumps(locations) if locations else None, 
            json.dumps(organizations) if organizations else None, 
            json.dumps(persons) if persons else None, 
            language,
            entry_id))

        # every 50 entries, commit the changes
        if i % 50 == 0:
            conn.commit()
        
    conn.close()
