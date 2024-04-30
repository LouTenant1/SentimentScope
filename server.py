from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
DATABASE_URI = os.environ.get("DATABASE_URI")
SECRET_KEY = os.environ.get("SECRET_KEY")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class SentimentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(128), nullable=False)
    sentiment = db.Column(db.String(32), nullable=False)

with app.app_context():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != SECRET_KEY:
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

executor = ThreadPoolExecutor(2)

def get_sentiment(data):
    return "Positive"

@app.route('/api/data', methods=['POST'])
@token_required
def submit_data():
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "Data is required!"}), 400
    sentiment = executor.submit(get_sentiment, data).result()
    sentiment_data = SentimentData(data=data, sentiment=sentiment)
    db.session.add(sentiment_data)
    db.session.commit()
    return jsonify({"message": "Data submitted successfully", "sentiment": sentiment}), 201

@app.route('/api/data', methods=['GET'])
@token_required
def fetch_data():
    sentiments = SentimentData.query.all()
    results = []
    for sentiment in sentiments:
        obj = {"id": sentiment.id, "data": sentiment.data, "sentiment": sentiment.sentiment}
        results.append(obj)
    return jsonify(results), 200

@app.route('/api/statistics', methods=['GET'])
@token_required
def statistics():
    total = SentimentData.query.count()
    positive = SentimentData.query.filter_by(sentiment="Positive").count()
    return jsonify({
        "total": total,
        "positive_sentiments": positive,
        "negative_sentiments": total - positive
    }), 200

if __name__ == '__main__':
    app.run(debug=True)