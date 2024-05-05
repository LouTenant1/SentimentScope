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
from joblib import dump, load
import hashlib

nlp = spacy.load("en_core_web_sm")

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.model = None
        # Dictionary to store cached preprocessed texts
        self.text_cache = {}

    def nltk_analyze(self, text):
        score = self.sia.polarity_scores(text)
        if score['compound'] > 0:
            return 'positive'
        elif score['compound'] < 0:
            return 'negative'
        else:
            return 'neutral'

    def spacy_preprocess(self, text):
        # Creating a hash of the text to use as a key for caching
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if text_hash in self.text_cache:
            return self.text_cache[text_hash]

        doc = nlp(text)
        tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        processed_text = ' '.join(tokens)
        self.text_cache[text_hash] = processed_text
        return processed_text

    def train_classifier(self, data_path):
        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            print(f"The file {data_path} was not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the dataset: {str(e)}")
            return
        
        try:
            df['processed_text'] = df['text'].apply(self.spacy_preprocess)
            X = df['processed_text']
            y = df['sentiment']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=1000))
            self.model.fit(X_train, y_train)
            predictions = self.model.predict(X_test)
            print(classification_report(y_test, predictions))

            # Saving the model
            dump(self.model, 'sentiment_model.joblib')
        except Exception as e:
            print(f"An error occurred during training: {str(e)}")

    def predict(self, text):
        if not self.model:
            try:
                # Attempt to load the model from disk if not already loaded
                self.model = load('sentiment_model.joblib')
            except FileNotFoundError:
                print("Model is not trained or loaded. Call train_classifier() first or ensure the model file exists.")
                return "Error: Model not loaded"
            except Exception as e:
                print(f"An error occurred while loading the model: {str(e)}")
                return "Error: Model load failure"

        processed_text = self.spacy_preprocess(text)
        try:
            return self.model.predict([processed_text])[0]
        except Exception as e:
            print(f"An error occurred during prediction: {str(e)}")
            return "Error: Prediction failure"

    def evaluate_new_data(self, data_path):
        # Ensure the model is loaded or trained
        if not self.model:
            try:
                self.model = load('sentiment_model.joblib')
            except FileNotFoundError:
                print("Model is not trained or loaded. Train or load the model first.")
                return
            except Exception as e:
                print(f"Could not load the model: {str(e)}")
                return

        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            print(f"The file {data_path} was not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the dataset: {str(e)}")
            return

        try:
            df['processed_text'] = df['text'].apply(self.spacy_preprocess)
            X = df['processed_text']
            y = df['sentiment']
            predictions = self.model.predict(X)
            print(classification_report(y, predictions))
        except Exception as e:
            print(f"An error occurred during evaluation: {str(e)}")

if __name__ == "__main__":
    DATA_PATH = os.getenv('DATA_PATH', 'path/to/your/dataset.csv')

    analyzer = SentimentAnalyzer()

    # Train or simply load the model for prediction
    # Uncomment the following line if training for the first time
    # analyzer.train_classifier(DATA_PATH)

    example_feedback = "This product has been excellent in my experience, I definitely recommend it!"
    sentiment = analyzer.predict(example_feedback)
    if not sentiment.startswith("Error"):
        print(f"Sentiment: {sentiment}")
    else:
        print(sentiment)

    # Evaluate the model on a new dataset (optional)
    # NEW_DATA_PATH = 'path/to/new/dataset.csv'
    # analyzer.evaluate_new_data(NEW_DATA_PATH)