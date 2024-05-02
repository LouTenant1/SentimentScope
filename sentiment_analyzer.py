import os
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np

nlp = spacy.load("en_core_web_sm")

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.model = None

    def nltk_analyze(self, text):
        score = self.sia.polarity_scores(text)
        if score['compound'] > 0:
            return 'positive'
        elif score['compound'] < 0:
            return 'negative'
        else:
            return 'neutral'

    def spacy_preprocess(self, text):
        doc = nlp(text)
        tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        return ' '.join(tokens)

    def train_classifier(self, data_path):
        df = pd.read_csv(data_path)
        df['processed_text'] = df['text'].apply(self.spacy_preprocess)
        X = df['processed_text']
        y = df['sentiment']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=1000))
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        print(classification_report(y_test, predictions))

    def predict(self, text):
        if not self.model:
            raise ValueError("Model is not trained. Call train_classifier() first.")
        processed_text = self.spacy_preprocess(text)
        return self.model.predict([processed_text])[0]

if __name__ == "__main__":
    DATA_PATH = os.getenv('DATA_PATH', 'path/to/your/dataset.csv')

    analyzer = SentimentAnalyzer()
    analyzer.train_classifier(DATA_PATH)
    example_feedback = "This product has been excellent in my experience, I definitely recommend it!"
    print(f"Sentiment: {analyzer.predict(example_feedback)}")