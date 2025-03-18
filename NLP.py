from transformers import pipeline, AutoTokenizer
import sqlite3
import json
import re
from camel_tools.ner import NERecognizer
from camel_tools.tokenizers.word import simple_word_tokenize


class belaNER():
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")
        self.max_length = self.tokenizer.model_max_length  # commonly 512 for BERT-based models
        self.chunk_size = self.max_length - 2  # reserve space for [CLS] and [SEP]
        self.ner = pipeline('ner', model='CAMeL-Lab/bert-base-arabic-camelbert-mix-ner', aggregation_strategy="none")
        

    def language_detection(self, sentence):
        if not hasattr(self, 'papluca'):
            # Load the language detection pipeline
            self.papluca = pipeline(
                'text-classification',
                model='papluca/xlm-roberta-base-language-detection')
        
        # Detect the language of the input sentence
        language = self.papluca(sentence[0:50])[0]['label']
        
        return language

    def clean(self, sentence):
        """Cleans text by removing special characters, HTML, URLs, and emojis."""
        sentence = re.sub(r'http\S+', ' ', sentence)  # Remove URLs
        sentence = re.sub(r'<.*?>', ' ', sentence)  # Remove HTML tags
        sentence = sentence.replace("#", "").replace("@", "").replace("\t", " ").replace("\r", " ").replace("\n", " ")
        return re.sub(r'\s+', ' ', sentence).strip()  # Remove extra spaces
    
    def chunk(self, text):
        # Tokenize the provided text
        tokens = self.tokenizer.tokenize(text)
        # Create token chunks of size 'chunk_size'
        token_chunks = [tokens[i:i+self.chunk_size] for i in range(0, len(tokens), self.chunk_size)]
        # Convert token chunks back to text
        text_chunks = [self.tokenizer.convert_tokens_to_string(chunk) for chunk in token_chunks]
        return text_chunks
    
    def extract_entities(self, text):
        # Chunk the text to ensure no input exceeds the token limit
        chunks = self.chunk(text)
        all_entities = []
        # Process each chunk separately with the NER pipeline
        for chunk in chunks:
            entities = self.ner(chunk)
            for entity in entities:
                # Round the score for clarity
                entity['score'] = round(float(entity['score']), 2)
            all_entities.extend(entities)
            
        # for entity in entity 
        merged_entities = []
    
        for entity in entities:
            # If the token starts with "##", merge with the previous entity if available
            if entity['word'].startswith("##") and merged_entities:
                # Remove the "##" prefix and append the text to the previous token's 'word'
                merged_entities[-1]['word'] += entity['word'][2:]
                # Update the end index to reflect the end of the merged token
                merged_entities[-1]['end'] = entity['end']
                # Optionally, update the score (here we take the average)
                merged_entities[-1]['score'] = round(
                    (merged_entities[-1]['score'] + entity['score']) / 2, 2
                )
            else:
                merged_entities.append(entity)
                
        return merged_entities
 
conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()


# Retrieve the 10 most recent entries (assuming 'id' represents the order)
cursor.execute("SELECT id, title, summary FROM entries ORDER BY published DESC LIMIT 100")
rows = cursor.fetchall()

ner_extractor = belaNER()


# Process each entry to extract entities and update the database
for row in rows:
    
    entry_id, title, summary = row
    
    # set the language of the sentence
    title = ner_extractor.clean(title)
    summary = ner_extractor.clean(summary)
    
    language = ner_extractor.language_detection(title)
    cursor.execute("UPDATE entries SET language = ? WHERE id = ?", (language, entry_id))
    
    
    print(title)
    
    if language == 'ar':
        print("Extracting entities from the sentence:", title)
        entities = ner_extractor.extract_entities(title)
        print("Entities:", entities)
        cursor.execute("UPDATE entries SET entities = ? WHERE id = ?", (json.dumps(entities), entry_id))
    else:
        cursor.execute("UPDATE entries SET entities = ? WHERE id = ?", (json.dumps([]), entry_id))
    

conn.commit()
conn.close()
