import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pathlib

current_dir = pathlib.Path(__file__).parent.resolve()

load_dotenv(os.path.join(current_dir, '.env'))

class Config:
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("No DATABASE_URL set in environment variables")
    
    # API configuration
    API_VERSION = '1.0'
    API_PREFIX = '/api/v1'
    
    # Metrics configuration
    METRICS_WINDOW_MONTHS = 3
    EMV_FOLLOWER_RATE = 2.1
    EMV_COMMENT_RATE = 4.19
    EMV_LIKE_RATE = 0.09
    EMV_PLAY_RATE = 0.11
    
    # Content detection
    PAID_CONTENT_KEYWORDS = ['@', 'اعلان']