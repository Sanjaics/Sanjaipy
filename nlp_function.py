from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import spacy
import torch

def analyze_sentiment(text):
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')

    encoded_text = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=512,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )

    with torch.no_grad():
        output = model(**encoded_text)

    scores = output[0].numpy()[0]
    sentiment_score = float(scores[1]) - float(scores[0])
    sentiment_label = None

    if sentiment_score > 5.0:
        sentiment_label = 'Good Day'
    elif sentiment_score < -5.0:
        sentiment_label = 'Bad Day'
    else:
        sentiment_label = 'Ordinary Day'

    return sentiment_score

def fetch_character_and_text(text):
    # Load pre-trained NER model
    nlp = spacy.load('en_core_web_sm')

    # Parse text with NER model
    doc = nlp(text)

    # Create empty list to store character and text tuples
    character_text_list = []

    # Loop through named entities in text
    for ent in doc.ents:
        # Check if named entity is a person
        if ent.label_ == 'PERSON':
            # Get character name
            character_name = ent.text

            # Get sentence containing named entity
            sentence = ent.sent.text

            # Append character and text tuple to list
            character_text_list.append((character_name, sentence))

    # Return list of character and text tuples
    return character_text_list
