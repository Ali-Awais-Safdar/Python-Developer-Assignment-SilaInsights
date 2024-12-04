from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import pandas as pd
import io
import logging
from metrics_calculator import MetricsCalculator
from database import Database
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Creator Metrics API", version=Config.API_VERSION)
db = Database()
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Creator Metrics API is running", "version": Config.API_VERSION}

@app.post("/api/v1/metrics/compute")
async def compute_metrics(
    profile_file: UploadFile = File(...),
    posts_file: UploadFile = File(...)
) -> Dict:
    try:
        # Read CSV files
        try:
            profile_content = await profile_file.read()
            posts_content = await posts_file.read()
            
            profile_df = pd.read_csv(io.StringIO(profile_content.decode()))
            posts_df = pd.read_csv(io.StringIO(posts_content.decode()))
        except Exception as e:
            logger.error(f"Error reading CSV files: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error reading CSV files: {str(e)}"
            )

        # Validate input data
        if len(profile_df) == 0:
            raise HTTPException(status_code=400, detail="Profile data is empty")
        if len(posts_df) == 0:
            raise HTTPException(status_code=400, detail="Posts data is empty")

        # Validate required columns in profile data
        required_profile_columns = ['username', 'profile_url', 'country', 'followers']
        missing_profile_columns = [col for col in required_profile_columns if col not in profile_df.columns]
        if missing_profile_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns in profile data: {missing_profile_columns}"
            )

        # Validate required columns in posts data
        required_posts_columns = [
            'description', 'pub_date', 'like_count', 'comment_count',
            'view_count', 'play_count', 'product_type', 'saves'
        ]
        missing_posts_columns = [col for col in required_posts_columns if col not in posts_df.columns]
        if missing_posts_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns in posts data: {missing_posts_columns}"
            )

        # Calculate metrics
        calculator = MetricsCalculator(posts_df, profile_df)
        overall_metrics, content_type_metrics = calculator.calculate_metrics()

        # Save to database
        success = db.save_metrics(overall_metrics, content_type_metrics)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save metrics to database"
            )

        return {
            "message": "Metrics computed and saved successfully",
            "overall_metrics": overall_metrics,
            "content_type_metrics": content_type_metrics
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error computing metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error computing metrics: {str(e)}"
        )

@app.get("/api/v1/metrics/{username}")
async def get_metrics(username: str) -> Dict:
    try:
        metrics = db.get_metrics(username)
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for username: {username}"
            )
            
        return metrics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving metrics: {str(e)}"
        )

@app.delete("/api/v1/metrics/{username}")
async def delete_metrics(username: str) -> Dict:
    try:
        success = db.delete_metrics(username)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for username: {username}"
            )
            
        return {"message": f"Metrics for username {username} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting metrics: {str(e)}"
        )

@app.get("/api/v1/health")
async def health_check():
    try:
        # Check database connection
        db.check_connection()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )