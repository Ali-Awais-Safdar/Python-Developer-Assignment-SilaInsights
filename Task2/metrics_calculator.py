import pandas as pd
from datetime import datetime, timezone
from typing import Tuple, Dict, List
from config import Config

class MetricsCalculator:
    def __init__(self, posts_df: pd.DataFrame, profile_df: pd.DataFrame):
        self.posts_df = posts_df
        self.profile_df = profile_df
        
        self.posts_df['pub_date'] = pd.to_datetime(self.posts_df['pub_date'], utc=True, errors='coerce')

        # Convert timezone-aware dates to UTC
        self.posts_df['pub_date'] = self.posts_df['pub_date'].dt.tz_convert('UTC').dt.tz_localize(None)

        # Get date range in UTC
        self.start_date, self.end_date = self._get_date_range()
        
        # Filter posts for last 3 months
        self.recent_posts = self.posts_df[
            (self.posts_df['pub_date'] >= self.start_date) & 
            (self.posts_df['pub_date'] <= self.end_date)
        ]
        
        # Determine paid vs organic content
        self.recent_posts['is_paid'] = self.recent_posts['description'].apply(
            lambda x: any(keyword in str(x).lower() for keyword in Config.PAID_CONTENT_KEYWORDS)
        )

    def _get_date_range(self):
        """Get date range in UTC without timezone info"""
        end_date = datetime.now(timezone.utc).replace(tzinfo=None)
        start_date = end_date - pd.Timedelta(days=90)
        return start_date, end_date
    
    def calculate_active_reach(self, posts: pd.DataFrame) -> float:
        if len(posts) == 0:
            return 0.0
        total_engagement = (
            posts['comment_count'].fillna(0) +
            posts['like_count'].fillna(0) +
            posts['view_count'].fillna(0)
        ).sum()
        return total_engagement / len(posts)

    def calculate_emv(self, posts: pd.DataFrame) -> float:
        followers = self.profile_df['followers'].iloc[0]
        total_comments = posts['comment_count'].fillna(0).sum()
        total_likes = posts['like_count'].fillna(0).sum()
        total_plays = posts['play_count'].fillna(0).sum()
        
        return (
            (followers / 1000 * Config.EMV_FOLLOWER_RATE) +
            (total_comments * Config.EMV_COMMENT_RATE) +
            (total_likes * Config.EMV_LIKE_RATE) +
            (total_plays * Config.EMV_PLAY_RATE)
        )

    def calculate_average_engagements(self, posts: pd.DataFrame) -> float:
        if len(posts) == 0:
            return 0.0
        total_engagement = (
            posts['like_count'].fillna(0) +
            posts['comment_count'].fillna(0) +
            posts['share_count'].fillna(0) +
            posts['saves'].fillna(0)
        ).sum()
        return total_engagement / len(posts)

    def calculate_metrics(self) -> Tuple[Dict, List[Dict]]:
        overall_metrics = {
            'username': str(self.profile_df['username'].iloc[0]),
            'profile_url': str(self.profile_df['profile_url'].iloc[0]),
            'country': str(self.profile_df['country'].iloc[0]),
            'followers': int(self.profile_df['followers'].iloc[0]),
            'active_reach': float(self.calculate_active_reach(self.recent_posts)),
            'emv': float(self.calculate_emv(self.recent_posts)),
            'avg_engagements': float(self.calculate_average_engagements(self.recent_posts)),
            'avg_video_views': float(
                self.recent_posts['view_count'].fillna(0).sum() / 
                len(self.recent_posts) if len(self.recent_posts) > 0 else 0
            ),
            'avg_story_reach': 0.0,
            'avg_story_engagements': 0.0,
            'avg_story_views': 0.0,
            'avg_saves': float(
                self.recent_posts['saves'].fillna(0).sum() / 
                len(self.recent_posts) if len(self.recent_posts) > 0 else 0
            ),
            'avg_likes': float(
                self.recent_posts['like_count'].fillna(0).sum() / 
                len(self.recent_posts) if len(self.recent_posts) > 0 else 0
            ),
            'avg_comments': float(
                self.recent_posts['comment_count'].fillna(0).sum() / 
                len(self.recent_posts) if len(self.recent_posts) > 0 else 0
            ),
            'avg_shares': float(
                self.recent_posts['share_count'].fillna(0).sum() / 
                len(self.recent_posts) if len(self.recent_posts) > 0 else 0
            ),
            'total_posts': int(len(self.recent_posts))
        }

        # Calculate metrics by content type
        content_type_metrics = []
        for is_paid in [True, False]:
            for media_type in ['Video', 'Photo']:
                filtered_posts = self.recent_posts[
                    (self.recent_posts['is_paid'] == is_paid) &
                    (self.recent_posts['product_type'] == media_type)
                ]
                
                if len(filtered_posts) > 0:
                    metrics = {
                        'username': str(self.profile_df['username'].iloc[0]),
                        'content_type': 'paid' if is_paid else 'organic',
                        'media_type': media_type.lower(),
                        'active_reach': float(self.calculate_active_reach(filtered_posts)),
                        'emv': float(self.calculate_emv(filtered_posts)),
                        'avg_engagements': float(self.calculate_average_engagements(filtered_posts)),
                        'avg_video_views': float(
                            filtered_posts['view_count'].fillna(0).sum() / 
                            len(filtered_posts)
                        ),
                        'avg_saves': float(
                            filtered_posts['saves'].fillna(0).sum() / 
                            len(filtered_posts)
                        ),
                        'avg_likes': float(
                            filtered_posts['like_count'].fillna(0).sum() / 
                            len(filtered_posts)
                        ),
                        'avg_comments': float(
                            filtered_posts['comment_count'].fillna(0).sum() / 
                            len(filtered_posts)
                        ),
                        'avg_shares': float(
                            filtered_posts['share_count'].fillna(0).sum() / 
                            len(filtered_posts)
                        ),
                        'total_posts': int(len(filtered_posts))
                    }
                    content_type_metrics.append(metrics)
        
        return overall_metrics, content_type_metrics