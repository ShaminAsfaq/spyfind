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
    CommentResponse, CommentCreate,
    DemonstrationRequest,
    HashtagAnalysisResponse, HashtagAnalysisUser
)
from app import crud
from app.models import BotDetection

router = APIRouter(prefix="/api", tags=["api"])


# ============================================================================
# DEMONSTRATION ENDPOINT
# ============================================================================

@router.post("/demonstrate")
def demonstrate(request: DemonstrationRequest, db: Session = Depends(get_db)):
    """
    Demonstration feature: Create bots, seed tweets, and inject hashtags.
    """
    import random
    import string
    
    # 1. Load bot data
    bot_csv_path = os.path.join(os.path.dirname(__file__), "..", "data_source", "social_spambots_1.csv", "users.csv")
    if not os.path.exists(bot_csv_path):
        raise HTTPException(status_code=500, detail="Bot data source not found")
    
    try:
        df = pd.read_csv(bot_csv_path)
        # Filter out some usable bots
        available_bots = df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading bot data: {str(e)}")

    if not available_bots:
        raise HTTPException(status_code=500, detail="No bots found in data source")

    # 2. Process hashtags
    hashtag_list = [h.strip().lstrip('#') for h in request.hashtags.split(',') if h.strip()]
    
    created_users = []
    total_tweets_created = 0

    for _ in range(request.num_bots):
        # Pick a random bot template
        bot_template = random.choice(available_bots)
        
        base_username = str(bot_template.get('screen_name', 'bot_user'))
        display_name = str(bot_template.get('name', 'Bot User'))
        
        # Handle uniqueness
        username = base_username
        while crud.get_user_by_username(db, username):
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            username = f"{base_username}_{suffix}"
        
        # Create User object
        user_in = UserCreate(
            username=username,
            display_name=display_name,
            bio=str(bot_template.get('description', ''))[:160] if pd.notna(bot_template.get('description')) else "",
            location=str(bot_template.get('location', ''))[:30] if pd.notna(bot_template.get('location')) else "",
            followers_count=int(bot_template.get('followers_count', 0)) if pd.notna(bot_template.get('followers_count')) else 0,
            following_count=int(bot_template.get('friends_count', 0)) if pd.notna(bot_template.get('friends_count')) else 0,
            posts_count=request.num_posts, # Set to match actual created posts
            likes_count=0,
            retweets_count=0,
            profile_image_url=bot_template.get('profile_image_url') if pd.notna(bot_template.get('profile_image_url')) else None
        )
        
        db_user = crud.create_user(db, user_in)
        
        # MANUALLY UPDATE BotDetection to True and set source
        bot_status = db.query(BotDetection).filter(BotDetection.user_id == db_user.id).first()
        if bot_status:
            bot_status.is_bot = True
            bot_status.source = "demonstration_panel"
            db.commit()
        
        created_users.append(db_user)
        
        # 3. Create posts for this bot
        bot_tweet_contents = [
            "Just setting up my roar! #newbie",
            "This simulation is interesting.",
            "Testing the bot detector functionality.",
            "I love sharing automated updates!",
            "Did you know that bots can be helpful too?",
            "Analyzing the latest trends in social media.",
            "Hello world! I am a simulated account.",
            "Looking for new friends to follow.",
            "Sharing some interesting facts today.",
            "Automated post for demonstration purposes."
        ]
        
        for i in range(request.num_posts):
            base_content = random.choice(bot_tweet_contents)
            
            # Add random hashtags from the list
            if hashtag_list:
                num_tags = random.randint(1, min(3, len(hashtag_list)))
                selected_tags = random.sample(hashtag_list, num_tags)
                tag_str = " " + " ".join([f"#{t}" for t in selected_tags])
                content = f"{base_content}{tag_str}"
            else:
                content = base_content
            
            tweet_in = TweetCreate(
                content=content,
                author_id=db_user.id
            )
            crud.create_tweet(db, tweet_in)
            total_tweets_created += 1

    return {
        "message": f"Successfully created {request.num_bots} bots and {total_tweets_created} total posts.",
        "bots_created": len(created_users),
        "posts_created": total_tweets_created
    }


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


def _perform_bot_prediction(user, model):
    """Internal helper to run model on a user object."""
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
        return _perform_bot_prediction(user, model)
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


@router.get("/hashtags/search/{query}", response_model=List[HashtagSummaryResponse])
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


# ============================================================================
# HASHTAG ANALYSIS ENDPOINT
# ============================================================================

@router.get("/hashtags/{hashtag_id}/analyze", response_model=HashtagAnalysisResponse)
def analyze_hashtag(hashtag_id: int, db: Session = Depends(get_db)):
    """
    Detailed hashtag analysis: 
    1. Find all unique users who used the hashtag
    2. Run each through the bot detector
    3. Return aggregated statistics and user details
    """
    hashtag = crud.get_hashtag(db, hashtag_id)
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    tweets = hashtag.tweets
    unique_users = {}
    for t in tweets:
        if t.author_id not in unique_users:
            unique_users[t.author_id] = t.author

    model_path = os.path.join(os.path.dirname(__file__), "..", "model", "bot_detector.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=500, detail="ML model not found")

    try:
        model = joblib.load(model_path)
        
        analysis_users = []
        bot_count = 0
        human_count = 0
        
        for user_id, user in unique_users.items():
            prediction_result = _perform_bot_prediction(user, model)
            
            is_bot = prediction_result["is_bot"]
            if is_bot:
                bot_count += 1
            else:
                human_count += 1
                
            analysis_users.append(HashtagAnalysisUser(
                id=user.id,
                username=user.username,
                display_name=user.display_name,
                prediction=prediction_result["prediction"],
                is_bot=is_bot,
                confidence=prediction_result["confidence"]
            ))

        total_users = len(unique_users)
        bot_percentage = (bot_count / total_users * 100) if total_users > 0 else 0

        return HashtagAnalysisResponse(
            hashtag_id=hashtag.id,
            hashtag_name=hashtag.name,
            total_tweets=len(tweets),
            total_users=total_users,
            bot_count=bot_count,
            human_count=human_count,
            bot_percentage=round(bot_percentage, 2),
            users=analysis_users
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
