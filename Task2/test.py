from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from models import Base, CreatorMetrics, ContentTypeMetrics
from sqlalchemy import inspect

load_dotenv()

database_url = os.getenv('DATABASE_URL')

try:
    engine = create_engine(database_url)
    
    Base.metadata.create_all(engine)
    
    # Try to connect
    with engine.connect() as connection:
        print("Successfully connected to the database!")
        
        # Verify table creation
        inspector = inspect(engine)
        print("Tables created:", inspector.get_table_names())
        
except Exception as e:
    print(f"Error connecting to the database: {str(e)}")