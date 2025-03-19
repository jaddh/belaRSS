from transformers import pipeline

# Use a distilled multilingual NER model
ner_pipeline = pipeline("ner", model="Davlan/distilbert-base-multilingual-cased-ner-hrl")

text = "RT Zaina Erhaim 🪬: After a hellish night of the #Israel bombing & mourning its three martyrs. This is #Daraa tonight celebrating the anniversary of..."
entities = ner_pipeline(text)
print(entities)

[{'entity': 'B-ORG', 'score': 0.9964174, 'index': 1, 'word': 'RT', 'start': 0, 'end': 2}, {'entity': 'I-ORG', 'score': 0.99045825, 'index': 2, 'word': 'Za', 'start': 3, 'end': 5}, {'entity': 'I-ORG', 'score': 0.9234632, 'index': 3, 'word': '##ina', 'start': 5, 'end': 8}, {'entity': 'I-ORG', 'score': 0.5934595, 'index': 4, 'word': 'Er', 'start': 9, 'end': 11}, {'entity': 'I-LOC', 'score': 0.42126003, 'index': 5, 'word': '##hai', 'start': 11, 'end': 14}, {'entity': 'I-ORG', 'score': 0.6481268, 'index': 6, 'word': '##m', 'start': 14, 'end': 15}, {'entity': 'B-LOC', 'score': 0.999741, 'index': 17, 'word': 'Israel', 'start': 49, 'end': 55}, {'entity': 'B-LOC', 'score': 0.8473426, 'index': 32, 'word': 'Dara', 'start': 103, 'end': 107}, {'entity': 'I-LOC', 'score': 0.84857243, 'index': 33, 'word': '##a', 'start': 107, 'end': 108}]