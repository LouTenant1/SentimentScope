from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")
SECRET_API_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SentimentRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_data = db.Column(db.String(128), nullable=False)
    text_sentiment = db.Column(db.String(32), nullable=False)

with app.app_context():
    db.create_all()

def requires_authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_token = request.headers.get('Authorization')
        if not provided_token or provided_token != SECRET_API_KEY:
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

executor = ThreadPoolExecutor(2)

def analyze_sentiment(text):
    return "Positive"

@app.route('/api/sentiment', methods=['POST'])
@requires_authorization
def submit_text_sentiment():
    text = request.json.get('data')
    if not text:
        return jsonify({"error": "Data is required!"}), 400

    analyzed_sentiment = executor.submit(analyze_sentiment, text).result()

    new_sentiment_record = SentimentRecord(text_data=text, text_sentiment=analyzed_sentiment)
    db.session.add(new_sentiment_record)
    db.session.commit()

    return jsonify({"message": "Data submitted successfully", "sentiment": analyzed_sentiment}), 201

@app.route('/api/sentiment', methods=['GET'])
@requires_authorization
def retrieve_sentiments():
    all_sentiments = SentimentRecord.query.all()
    sentiment_results = [
        {"id": record.id, "data": record.text_data, "sentiment": record.text_sentiment} for record in all_sentiments
    ]
    return jsonify(sentiment_results), 200

@app.route('/api/sentiment-statistics', methods=['GET'])
@requires_authorization
def sentiment_statistics():
    sentiments_count = SentimentRecord.query.count()
    positive_count = SentimentRecord.query.filter_by(text_sentiment="Positive").count()
    negative_count = sentiments_count - positive_count
    return jsonify({
        "total": sentiments_count,
        "positive_sentiments": positive_count,
        "negative_sentiments": negative_count
    }), 200

if __name__ == '__main__':
    app.run(debug=True)