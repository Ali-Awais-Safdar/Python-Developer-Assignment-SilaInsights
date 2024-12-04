from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class CreatorMetrics(Base):
    __tablename__ = 'creator_metrics'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    profile_url = Column(String)
    country = Column(String)
    followers = Column(Integer)
    active_reach = Column(Float)
    emv = Column(Float)
    avg_engagements = Column(Float)
    avg_video_views = Column(Float)
    avg_story_reach = Column(Float)
    avg_story_engagements = Column(Float)
    avg_story_views = Column(Float)
    avg_saves = Column(Float)
    avg_likes = Column(Float)
    avg_comments = Column(Float)
    avg_shares = Column(Float)
    total_posts = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ContentTypeMetrics(Base):
    __tablename__ = 'content_type_metrics'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    content_type = Column(String)
    media_type = Column(String)
    active_reach = Column(Float)
    emv = Column(Float)
    avg_engagements = Column(Float)
    avg_video_views = Column(Float)
    avg_saves = Column(Float)
    avg_likes = Column(Float)
    avg_comments = Column(Float)
    avg_shares = Column(Float)
    total_posts = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

