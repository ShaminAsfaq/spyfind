"""FastAPI routes for Spyfind API."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import os
import joblib
import pandas as pd

from app.database import get_db
from app.schemas import (
    UserResponse, UserCreate,
    HashtagResponse, HashtagDetailResponse, HashtagSummaryResponse,
    TweetResponse, TweetCreate, TweetListResponse,
    RepostResponse, RepostCreate,
    CommentResponse, CommentCreate
)
from app import crud

router = APIRouter(prefix="/api", tags=["api"])


# ============================================================================
# USER ENDPOINTS
# ============================================================================

@router.get("/users", response_model=List[UserResponse])
def list_users(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all users."""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, user)


@router.get("/users/{user_id}/tweets", response_model=List[TweetResponse])
def get_user_tweets(user_id: int, skip: int = Query(0), limit: int = Query(20), db: Session = Depends(get_db)):
    """Get all tweets by a specific user with pagination."""
    # Verify user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tweets = crud.get_tweets_by_user(db, user_id, skip=skip, limit=limit)
    return tweets


@router.get("/predict/{username}")
def predict_bot(username: str, db: Session = Depends(get_db)):
    """Predict if a user is a bot using the ML model."""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    model_path = os.path.join(os.path.dirname(__file__), "..", "model", "bot_detector.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=500, detail="ML model not found")

    try:
        model = joblib.load(model_path)
        
        # Calculate features
        statuses = user.posts_count or 0
        followers = user.followers_count or 0
        friends = user.following_count or 0
        reputation = followers / (followers + friends + 1)
        post_to_follower_ratio = statuses / (followers + 1)
        
        feature_names = ['statuses_count', 'followers_count', 'friends_count', 'reputation', 'post_to_follower_ratio']
        df = pd.DataFrame([[statuses, followers, friends, reputation, post_to_follower_ratio]], columns=feature_names)
        
        prediction = bool(model.predict(df)[0])
        
        confidence = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(df)
            confidence = int(max(probs[0]) * 100)

        return {
            "user_id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "prediction": "BOT" if prediction else "HUMAN",
            "is_bot": prediction,
            "confidence": confidence,
            "features": {
                "statuses_count": statuses,
                "followers_count": followers,
                "friends_count": friends,
                "reputation": round(reputation, 4),
                "post_to_follower_ratio": round(post_to_follower_ratio, 4)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ============================================================================
# HASHTAG ENDPOINTS
# ============================================================================

@router.get("/hashtags", response_model=List[HashtagResponse])
def list_hashtags(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all hashtags."""
    hashtags = crud.get_hashtags(db, skip=skip, limit=limit)
    return hashtags


@router.get("/hashtags/search/{query}", response_model=List[HashtagResponse])
def search_hashtags(query: str, exact: bool = Query(False), db: Session = Depends(get_db)):
    """Search hashtags by name."""
    hashtags = crud.search_hashtags(db, query, exact=exact)
    return hashtags


@router.get("/hashtags/top/tweets")
def get_top_hashtags_tweets(limit: int = Query(10), db: Session = Depends(get_db)):
    """Get top hashtags sorted by number of tweets."""
    hashtags = crud.get_top_hashtags_by_tweets(db, limit=limit)
    return {"top_hashtags": hashtags}


@router.get("/hashtags/top/date")
def get_top_hashtags_date(limit: int = Query(10), db: Session = Depends(get_db)):
    """Get top hashtags sorted by creation date (newest first)."""
    hashtags = crud.get_top_hashtags_by_date(db, limit=limit)
    return {"top_hashtags": hashtags}


@router.get("/hashtags/{hashtag_id}", response_model=HashtagDetailResponse)
def get_hashtag(hashtag_id: int, db: Session = Depends(get_db)):
    """Get hashtag details with associated tweets (Warning: loads ALL tweets)."""
    hashtag = crud.get_hashtag(db, hashtag_id)
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    return hashtag


@router.get("/hashtags/{hashtag_id}/summary", response_model=HashtagSummaryResponse)
def get_hashtag_summary(hashtag_id: int, db: Session = Depends(get_db)):
    """Get hashtag summary with tweet count."""
    hashtag = crud.get_hashtag(db, hashtag_id)
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    
    count = crud.count_tweets_by_hashtag(db, hashtag_id)
    
    return {
        "id": hashtag.id,
        "name": hashtag.name,
        "created_at": hashtag.created_at,
        "tweet_count": count
    }


@router.get("/hashtags/{hashtag_id}/tweets", response_model=TweetListResponse)
def get_hashtag_tweets_paginated(
    hashtag_id: int, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(20, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    """Get paginated tweets for a hashtag."""
    # Verify hashtag exists
    hashtag = crud.get_hashtag(db, hashtag_id)
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    
    tweets = crud.get_tweets_by_hashtag_paginated(db, hashtag_id, skip=skip, limit=limit)
    total = crud.count_tweets_by_hashtag(db, hashtag_id)
    
    return {
        "tweets": tweets,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ============================================================================
# TWEET ENDPOINTS
# ============================================================================

@router.get("/tweets", response_model=List[TweetResponse])
def list_tweets(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all tweets."""
    tweets = crud.get_tweets(db, skip=skip, limit=limit)
    return tweets


@router.get("/tweets/{tweet_id}", response_model=TweetResponse)
def get_tweet(tweet_id: int, db: Session = Depends(get_db)):
    """Get tweet details."""
    tweet = crud.get_tweet(db, tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return tweet


@router.post("/tweets", response_model=TweetResponse)
def create_tweet(tweet: TweetCreate, db: Session = Depends(get_db)):
    """
    Create a new tweet.

    Automatically extracts and creates hashtags from the tweet content.
    """
    # Verify user exists
    user = crud.get_user(db, tweet.author_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_tweet(db, tweet)


@router.post("/tweets/{tweet_id}/like", response_model=TweetResponse)
def like_tweet(tweet_id: int, db: Session = Depends(get_db)):
    """Like a tweet (increment like count)."""
    tweet = crud.like_tweet(db, tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return tweet


# ============================================================================
# REPOST ENDPOINTS
# ============================================================================

@router.post("/reposts", response_model=RepostResponse)
def create_repost(repost: RepostCreate, db: Session = Depends(get_db)):
    """
    Create a repost of a tweet.
    Increments the original tweet's retweets_count and the user's posts_count.
    """
    # Verify user exists
    user = crud.get_user(db, repost.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify tweet exists
    tweet = crud.get_tweet(db, repost.original_tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return crud.create_repost(db, repost)


@router.get("/reposts/user/{user_id}", response_model=List[RepostResponse])
def get_user_reposts(user_id: int, db: Session = Depends(get_db)):
    """Get all reposts by a specific user."""
    reposts = crud.get_reposts_by_user(db, user_id)
    return reposts


@router.get("/reposts/tweet/{tweet_id}", response_model=List[RepostResponse])
def get_tweet_reposts(tweet_id: int, db: Session = Depends(get_db)):
    """Get all reposts of a specific tweet."""
    reposts = crud.get_reposts_by_tweet(db, tweet_id)
    return reposts


# ============================================================================
# COMMENT ENDPOINTS
# ============================================================================

@router.post("/comments", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """
    Create a comment on a tweet.
    Increments the tweet's comments_count.
    """
    # Verify user exists
    user = crud.get_user(db, comment.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify tweet exists
    tweet = crud.get_tweet(db, comment.tweet_id)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return crud.create_comment(db, comment)


@router.get("/comments/tweet/{tweet_id}", response_model=List[CommentResponse])
def get_tweet_comments(tweet_id: int, db: Session = Depends(get_db)):
    """Get all comments for a specific tweet."""
    comments = crud.get_comments_by_tweet(db, tweet_id)
    return comments


@router.get("/comments/user/{user_id}", response_model=List[CommentResponse])
def get_user_comments(user_id: int, db: Session = Depends(get_db)):
    """Get all comments by a specific user."""
    comments = crud.get_comments_by_user(db, user_id)
    return comments
