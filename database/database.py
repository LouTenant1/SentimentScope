from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import os
from dotenv import load_dotenv
import logging
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    sentiments = relationship("SentimentAnalysisResult", back_populates="feedback")

class SentimentAnalysisResult(Base):
    __tablename__ = 'sentiment_analysis_results'
    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer, ForeignKey('feedback.id'), nullable=False)
    sentiment_score = Column(Float, nullable=False)
    sentiment = Column(String, nullable=False)
    feedback = relationship("Feedback", back_populates="sentiments")

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error("Session rolled back due to error: %s", str(e), exc_info=True)
        raise
    finally:
        session.close()

def create_tables():
    """Function to create database tables."""
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created successfully.")

def add_feedback(user_id, content):
    """Function to add feedback."""
    with session_scope() as session:
        new_feedback = Feedback(user_id=user_id, content=content)
        session.add(new_feedback)
        logging.info(f"New feedback added, ID: {new_feedback.id}")
        return new_feedback.id

def add_sentiment_analysis_result(feedback_id, sentiment_score, sentiment):
    """Function to add a sentiment analysis result."""
    with session_scope() as session:
        new_result = SentimentAnalysisResult(feedback_id=feedback_id, sentiment_score=sentiment_score, sentiment=sentiment)
        session.add(new_result)
        logging.info(f"New sentiment result added, ID: {new_result.id}")
        return new_result.id

def get_feedback_with_sentiments(feedback_id):
    """Function to get feedback along with its sentiments."""
    with session_scope() as session:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            logging.info(f"Feedback and sentiments fetched for ID: {feedback_id}")
            return {
                "user_id": feedback.user_id,
                "content": feedback.content,
                "sentiments": [{
                    "sentiment_score": s.sentiment_score,
                    "sentiment": s.sentiment
                } for s in feedback.sentiments]
            }
        logging.warning(f"No feedback found, ID: {feedback_id}")

def update_feedback(feedback_id, new_content):
    """Function to update feedback content."""
    with session_scope() as session:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            feedback.content = new_content
            logging.info(f"Feedback updated, ID: {feedback_id}")
            return True
        logging.warning(f"No feedback found to update, ID: {feedback_id}")
        return False

if __name__ == "__main__":
    create_tables()