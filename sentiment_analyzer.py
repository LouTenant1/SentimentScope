import os
import pandas as pd
import numpy as np
from joblib import dump, load
import hashlib
from datetime import datetime
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report

try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"An error occurred loading SpaCy's model: {e}")
    raise

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.model = None
        self.text_cache = {}

    def nltk_analyze(self, text):
        try:
            score = self.sia.polarity_scores(text)
            if score['compound'] > 0:
                return 'positive'
            elif score['compound'] < 0:
                return 'negative'
            else:
                return 'neutral'
        except Exception as e:
            print(f"An error occurred during NLTK analysis: {str(e)}")
            return "Error: NLTK analysis failure"

    @staticmethod
    def clean_text(text):
        text = re.sub(r'https?://\S+', '', text)  # Remove URLs
        text = re.sub(r'[^A-Za-z0-9\s]+', '', text)  # Remove non-alphanumeric characters
        return text

    def spacy_preprocess(self, text):
        try:
            text = self.clean_text(text)  # Cleaning text
            text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            if text_hash in self.text_cache:
                return self.text_cache[text_hash]

            doc = nlp(text)
            tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
            processed_text = ' '.join(tokens)
            self.text_cache[text_hash] = processed_text
            return processed_text
        except Exception as e:
            print(f"An error occurred during SpaCy preprocessing: {e}")
            return ""

    def train_classifier(self, data_path, force_retrain=False):
        model_path = 'sentiment_model.joblib'
        if os.path.exists(model_path) and not force_retrain:
            print("A trained model already exists. Set force_retrain=True to retrain.")
            return

        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            print(f"The file {data_path} was not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the dataset: {e}")
            return

        df['processed_text'] = df['text'].apply(self.spacy_preprocess)
        X = df['processed_text']
        y = df['sentiment']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        vectorizer_params = {'max_features': None}  # Customize your TfidfVectorizer params here
        model_params = {'max_iter': 1000}  # Customize your LogisticRegression params here

        self.model = make_pipeline(TfidfVectorizer(**vectorizer_params), LogisticRegression(**model_params))
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        print(classification_report(y_test, predictions))

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        model_filename = f'sentiment_model_{timestamp}.joblib'
        dump(self.model, model_filename)
        print(f"Model saved as {model_filename}")

    def predict(self, text):
        if not self.model:
            try:
                self.model = load('sentiment_model.joblib')
            except FileNotFoundError:
                print("Model is not trained or loaded. Call train_classifier() first or ensure the model file exists.")
                return "Error: Model not loaded"
            except Exception as e:
                print(f"An error occurred while loading the model: {e}")
                return "Error: Model load failure"

        processed_text = self.spacy_preprocess(text)
        try:
            prediction = self.model.predict([processed_text])[0]
            return prediction
        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return "Error: Prediction failure"

    def evaluate_new_data(self, data_path):
        if not self.model:
            try:
                self.model = load('sentiment_model.joblib')
            except FileNotFoundError:
                print("Model is not trained or loaded. Train or load the model first.")
                return
            except Exception as e:
                print(f"Could not load the model: {e}")
                return

        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            print(f"The file {data_path} was not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the data: {e}")
            return

        df['processed_text'] = df['text'].apply(self.spacy_preprocess)
        X = df['processed_text']
        y = df['sentiment']
        predictions = self.model.predict(X)
        print(classification_report(y, predictions))

if __name__ == "__main__":
    DATA_PATH = os.getenv('DATA_PATH', 'path/to/your/dataset.csv')
    analyzer = SentimentAnalyzer()

    # Example usage:
    force_retrain = False  # Change to True if you wish to retrain anyway
    if force_retrain or not os.path.exists('sentiment_model.joblib'):
        analyzer.train_classifier(DATA_PATH, force_retrain=force_retrain)

    example_feedback = "This product has been excellent in my experience, I definitely recommend it!"
    sentiment = analyzer.predict(example_feedback)
    if not sentiment.startswith("Error"):
        print(f"Sentiment: {sentiment}")
    else:
        print(sentiment)