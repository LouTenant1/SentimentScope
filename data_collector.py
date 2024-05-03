import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import json
import pymysql
from textblob import TextBlob

load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

def fetch_tweets(keyword, max_results=10):
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results={max_results}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises stored HTTPError, if occurred.
        return json.loads(response.text)['data']
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch tweets: {e}")
        return []

def fetch_feedback_from_db():
    try:
        connection = pymysql.connect(host=DATABASE_HOST,
                                     user=DATABASE_USER,
                                     password=DATABASE_PASSWORD,
                                     database=DATABASE_NAME,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM feedback")
            result = cursor.fetchall()
            return result
    except pymysql.MySQLError as e:
        print(f"Database connection failed: {e}")
        return []

def scrape_website(urls):
    all_comments = []
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises stored HTTPError, if occurred.
            soup = BeautifulSoup(response.text, 'html.parser')
            comments = soup.find_all(class_='feedback-comment-class')
            feedback_list = [comment.get_text().strip() for comment in comments]
            all_comments += feedback_list
        except requests.exceptions.RequestException as e:
            print(f"Failed to scrape {url}: {e}")
    return all_comments

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#','', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return 'positive' if analysis.sentiment.polarity > 0 else 'negative' if analysis.sentiment.polarity < 0 else 'neutral'

def collect_and_preprocess_data():
    tweets = fetch_tweets("customer feedback")
    feedback_db = fetch_feedback_from_db()
    scraped_feedback = scrape_website(["https://example.com/feedback", "https://anotherexample.com/comments"])

    all_cleaned_feedback = [
        {"text": clean_text(item['text']), "sentiment": analyze_sentiment(item['text'])} for item in tweets
    ] + [
        {"text": clean_text(item['text']), "sentiment": analyze_sentiment(item['text'])} for item in feedback_db
    ] + [
        {"text": clean_text(item), "sentiment": analyze_sentiment(item)} for item in scraped_feedback
    ]

    return all_cleaned_feedback

def save_data_to_file(data, filename='collected_feedback.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collected_data = collect_and_preprocess_data()
    print(collected_data)
    save_data_to_file(collected_data)