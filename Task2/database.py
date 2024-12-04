from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import CreatorMetrics, ContentTypeMetrics, Base
from config import Config
from typing import Dict, List, Optional
import logging
import numpy as np
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

def convert_numpy_to_python(value):
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    return value

class Database:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_metrics(self, overall_metrics: Dict, content_type_metrics: List[Dict]) -> bool:
        session = self.SessionLocal()
        try:
            converted_overall_metrics = {
                key: convert_numpy_to_python(value) 
                for key, value in overall_metrics.items()
            }

            converted_content_type_metrics = [
                {
                    key: convert_numpy_to_python(value) 
                    for key, value in metrics.items()
                }
                for metrics in content_type_metrics
            ]

            logger.info(f"Converted Overall Metrics: {converted_overall_metrics}")
            logger.info(f"Converted Content Type Metrics: {converted_content_type_metrics}")

            # Update or create overall metrics
            existing_metrics = session.query(CreatorMetrics).filter_by(
                username=converted_overall_metrics['username']
            ).first()

            if existing_metrics:
                for key, value in converted_overall_metrics.items():
                    if hasattr(existing_metrics, key):
                        setattr(existing_metrics, key, value)
            else:
                new_metrics = CreatorMetrics(**converted_overall_metrics)
                session.add(new_metrics)

            # Update or create content type metrics
            for metrics in converted_content_type_metrics:
                existing_content_metrics = session.query(ContentTypeMetrics).filter_by(
                    username=metrics['username'],
                    content_type=metrics['content_type'],
                    media_type=metrics['media_type']
                ).first()

                if existing_content_metrics:
                    for key, value in metrics.items():
                        if hasattr(existing_content_metrics, key):
                            setattr(existing_content_metrics, key, value)
                else:
                    new_content_metrics = ContentTypeMetrics(**metrics)
                    session.add(new_content_metrics)

            session.commit()
            logger.info("Metrics saved successfully")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            logger.error(f"Error details: {e.__dict__}")
            import traceback
            logger.error(traceback.format_exc())
            session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(traceback.format_exc())
            session.rollback()
            return False
        finally:
            session.close()

    def get_metrics(self, username: str) -> Optional[Dict]:
        session = self.SessionLocal()
        try:
            # Get overall metrics
            overall_metrics = session.query(CreatorMetrics).filter_by(
                username=username
            ).first()

            if not overall_metrics:
                return None

            # Get content type metrics
            content_metrics = session.query(ContentTypeMetrics).filter_by(
                username=username
            ).all()

            result = {
                'overall_metrics': {
                    column.name: getattr(overall_metrics, column.name)
                    for column in CreatorMetrics.__table__.columns
                    if column.name != 'id'
                },
                'content_type_metrics': [
                    {
                        column.name: getattr(metrics, column.name)
                        for column in ContentTypeMetrics.__table__.columns
                        if column.name != 'id'
                    }
                    for metrics in content_metrics
                ]
            }

            return result

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return None
        finally:
            session.close()

    def check_connection(self) -> bool:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection check failed: {str(e)}")
            raise

    def delete_metrics(self, username: str) -> bool:
        session = self.SessionLocal()
        try:
            # Delete from creator_metrics
            creator_deleted = session.query(CreatorMetrics).filter_by(
                username=username
            ).delete()
            
            # Delete from content_type_metrics
            content_deleted = session.query(ContentTypeMetrics).filter_by(
                username=username
            ).delete()
            
            session.commit()
            return creator_deleted > 0 or content_deleted > 0

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()