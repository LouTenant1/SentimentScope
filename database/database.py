from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

from contextlib import contextmanager

@contextmanager
def session_scope():
    logging.info("Starting a database session.")
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logging.info("Database session committed.")
    except:
        session.rollback()
        logging.error("Database session rolled back due to an error.", exc_info=True)
        raise
    finally:
        session.close()
        logging.info("Database session closed.")

def create_tables():
    logging.info("Creating database tables.")
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created successfully.")

def add_feedback(user_id, content):
    with session_scope() as session:
        logging.info(f"Adding new feedback for user_id: {user_id}")
        new_feedback = Feedback(user_id=user_id, content=content)
        session.add(new_feedback)
        session.flush()
        logging.info(f"New feedback added with ID: {new_feedback.id}")
        return new_feedback.id

def add_sentiment_analysis_result(feedback_id, sentiment_score, sentiment):
    with session_scope() as session:
        logging.info(f"Adding sentiment analysis result for feedback_id: {feedback_id}")
        new_result = SentimentAnalysisResult(
            feedback_id=feedback_id, sentiment_score=sentiment_score, sentiment=sentiment
        )
        session.add(new_result)
        session.flush()
        logging.info(f"New sentiment analysis result added with ID: {new_result.id}")
        return new_result.id

def get_feedback_with_sentiments(feedback_id):
    with session_scope() as session:
        logging.info(f"Fetching feedback with sentiments for feedback_id: {feedback_id}")
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            logging.info("Feedback found and returned with sentiments.")
            return {
                "user_id": feedback.user_id,
                "content": feedback.content,
                "sentiments": [
                    {"sentiment_score": s.sentiment_score, "sentiment": s.sentiment} for s in feedback.sentiments
                ]
            }
        else:
            logging.warning(f"No feedback found for ID: {feedback_id}")

def update_feedback(feedback_id, new_content):
    with session_scope() as session:
        logging.info(f"Updating feedback for feedback_id: {feedback_id}")
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            feedback.content = new_content
            logging.info(f"Feedback updated successfully for ID: {feedback_id}")
            return True
        else:
            logging.warning(f"No feedback found to update for ID: {feedback_id}")
            return False

if __name__ == "__main__":
    create_tables()