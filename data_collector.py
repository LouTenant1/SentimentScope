import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import json
import pymysql

load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

def fetch_tweets(keyword, max_results=10):
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    url = f"https://api.twitter.com/2/tweets/search/recent?query={keyword}&max_results={max_results}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)['data']
    else:
        print("Failed to fetch tweets")
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

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    comments = soup.find_all(class_='feedback-comment-class')
    feedback_list = [comment.get_text().strip() for comment in comments]
    
    return feedback_list

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#','', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

def collect_and_preprocess_data():
    tweets = fetch_tweets("customer feedback")
    clean_tweets = [clean_text(tweet['text']) for tweet in tweets]

    feedback_db = fetch_feedback_from_db()
    clean_feedback_db = [clean_text(feedback['text']) for feedback in feedback_db]

    scraped_feedback = scrape_website("https://example.com/feedback")
    clean_scraped_feedback = [clean_text(feedback) for feedback in scraped_feedback]

    all_cleaned_feedback = clean_tweets + clean_feedback_db + clean_scraped_feedback

    return all_cleaned_feedback

if __name__ == "__main__":
    collected_data = collect_and_preprocess_data()
    print(collected_data)