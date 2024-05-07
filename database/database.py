from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
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


# Context manager for session scope
from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    Base.metadata.create_all(bind=engine)


def add_feedback(user_id, content):
    with session_scope() as session:
        new_feedback = Feedback(user_id=user_id, content=content)
        session.add(new_feedback)
        session.flush()  # Immediately get the ID without waiting for commit
        return new_feedback.id


def add_sentiment_analysis_result(feedback_id, sentiment_score, sentiment):
    with session_scope() as session:
        new_result = SentimentAnalysisResult(
            feedback_id=feedback_id, sentiment_score=sentiment_score, sentiment=sentiment
        )
        session.add(new_result)
        session.flush()  # To get the ID
        return new_result.id


def get_feedback_with_sentiments(feedback_id):
    with session_scope() as session:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            return {
                "user_id": feedback.user_id,
                "content": feedback.content,
                "sentiments": [
                    {"sentiment_score": s.sentiment_score, "sentiment": s.sentiment} for s in feedback.sentiments
                ]
            }


def update_feedback(feedback_id, new_content):
    with session_scope() as session:
        feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
        if feedback:
            feedback.content = new_content
            return True
        return False


if __name__ == "__main__":
    create_tables()