from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
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


# Create session for database transactions
Session = sessionmaker(bind=engine)


def create_tables():
    """Create database tables based on models."""
    Base.metadata.create_all(engine)


def add_feedback(user_id, content):
    """Add a feedback entry to the database.

    Args:
    user_id (int): The ID of the user submitting feedback.
    content (str): The content of the feedback.

    Returns:
    int: The ID of the created feedback entry.
    """
    session = Session()
    new_feedback = Feedback(user_id=user_id, content=content)
    session.add(new_feedback)
    session.commit()
    return new_feedback.id


def add_sentiment_analysis_result(feedback_id, sentiment_score, sentiment):
    """Add a sentiment analysis result to the database.

    Args:
    feedback_id (int): The ID of the feedback to which the analysis belongs.
    sentiment_score (float): The numerical sentiment analysis score.
    sentiment (str): The label of the sentiment analysis result.

    Returns:
    int: The ID of the created sentiment analysis result.
    """
    session = Session()
    new_result = SentimentAnalysisResult(
        feedback_id=feedback_id, sentiment_score=sentiment_score, sentiment=sentiment
    )
    session.add(new_result)
    session.commit()
    return new_result.id


def get_feedback_with_sentiments(feedback_id):
    """Retrieve feedback along with its sentiment analysis results.

    Args:
    feedback_id (int): The ID of the feedback to retrieve.

    Returns:
    dict or None: A dictionary containing the feedback and its sentiments
                  if found, else None.
    """
    session = Session()
    feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback:
        return {
            "user_id": feedback.user_id,
            "content": feedback.content,
            "sentiments": [
                {"sentiment_score": s.sentiment_score, "sentiment": s.sentiment} for s in feedback.sentiments
            ]
        }
    else:
        return None


def update_feedback(feedback_id, new_content):
    """Update the content of an existing feedback entry.

    Args:
    feedback_id (int): The ID of the feedback to update.
    new_content (str): The new content to assign to the feedback.

    Returns:
    bool: True if the update was successful, False otherwise.
    """
    session = Session()
    feedback = session.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback:
        feedback.content = new_content
        session.commit()
        return True
    return False


if __name__ == "__main__":
    create_tables()