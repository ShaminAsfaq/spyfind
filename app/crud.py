"""CRUD operations for database models."""
import re
import random
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Tweet, Hashtag, Repost, Comment, BotDetection, tweet_hashtag_association
from app.schemas import UserCreate, TweetCreate, RepostCreate, CommentCreate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with realistic random stats."""
    # Generate random realistic colors
    profile_colors = ["#1da1f2", "#e74c3c", "#3498db", "#9b59b6", "#2ecc71", "#f39c12", "#34495e", "#e67e22", "#1abc9c", "#d35400"]
    banner_colors = ["#ffffff", "#f0f0f0", "#e8f5ff", "#fff3e0", "#f3e5f5", "#e8f8f5", "#fce4ec", "#e0f2f1"]

    # Generate realistic follower/following counts
    # Most users have between 10-5000 followers, with some having more
    followers = random.choices(
        [random.randint(10, 500), random.randint(500, 2000), random.randint(2000, 10000), random.randint(10000, 50000)],
        weights=[70, 20, 8, 2]
    )[0]

    # Following count typically ranges from 50-2000
    following = random.randint(50, min(2000, followers + 500))

    # Posts count between 100-10000
    posts = random.randint(100, 10000)

    # Likes received - typically higher than posts
    likes = random.randint(posts // 2, posts * 50)

    # Listed count - usually a fraction of followers
    listed = random.randint(0, max(1, followers // 10))

    db_user = User(
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        location=user.location,
        url=user.url if user.url else "",
        followers_count=user.followers_count if user.followers_count > 0 else followers,
        following_count=user.following_count if user.following_count > 0 else following,
        posts_count=user.posts_count if user.posts_count > 0 else posts,
        likes_count=user.likes_count if user.likes_count > 0 else likes,
        listed_count=user.listed_count if user.listed_count > 0 else listed,
        retweets_count=user.retweets_count if user.retweets_count > 0 else random.randint(0, 500),
        profile_color=user.profile_color if user.profile_color else random.choice(profile_colors),
        banner_color=user.banner_color if user.banner_color else random.choice(banner_colors),
        profile_image_url=user.profile_image_url,
        profile_banner_url=user.profile_banner_url
    )
    db.add(db_user)
    db.flush()

    # Add bot detection entry (default to human for manual creation)
    bot_status = BotDetection(
        user_id=db_user.id,
        is_bot=False,
        source="manual_creation"
    )
    db.add(bot_status)

    db.commit()
    db.refresh(db_user)
    return db_user


def get_tweets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Tweet]:
    """Get all tweets by a specific user with pagination, ordered by latest first."""
    return db.query(Tweet).filter(Tweet.author_id == user_id).order_by(Tweet.created_at.desc()).offset(skip).limit(limit).all()


def get_hashtag(db: Session, hashtag_id: int) -> Optional[Hashtag]:
    """Get hashtag by ID."""
    return db.query(Hashtag).filter(Hashtag.id == hashtag_id).first()


def get_hashtag_by_name(db: Session, name: str) -> Optional[Hashtag]:
    """Get hashtag by name (Case-Sensitive)."""
    return db.query(Hashtag).filter(Hashtag.name == name).first()


def get_hashtags(db: Session, skip: int = 0, limit: int = 100) -> List[Hashtag]:
    """Get all hashtags with pagination."""
    return db.query(Hashtag).offset(skip).limit(limit).all()


def create_hashtag(db: Session, name: str) -> Hashtag:
    """Create a new hashtag (or return existing one)."""
    # Check if hashtag already exists (case-insensitive)
    existing = get_hashtag_by_name(db, name)
    if existing:
        return existing

    db_hashtag = Hashtag(name=name)
    db.add(db_hashtag)
    db.commit()
    db.refresh(db_hashtag)
    return db_hashtag


def search_hashtags(db: Session, query: str, exact: bool = False) -> List[dict]:
    """Search hashtags by name (Case-Insensitive) including tweet count, prioritizing matches."""
    from sqlalchemy import func as sql_func, or_, case
    
    # Base query for selecting hashtag data and counting tweets
    query_obj = db.query(
        Hashtag.id,
        Hashtag.name,
        Hashtag.created_at,
        sql_func.count(tweet_hashtag_association.c.tweet_id).label('tweet_count')
    ).outerjoin(
        tweet_hashtag_association, Hashtag.id == tweet_hashtag_association.c.hashtag_id
    ).group_by(
        Hashtag.id, Hashtag.name, Hashtag.created_at
    )

    if exact:
        # For exact match, check both original and lowercase version if possible
        # Since we use BINARY collation, we check against the name directly
        results = query_obj.filter(
            or_(
                Hashtag.name == query,
                Hashtag.name == query.lower(),
                Hashtag.name == query.upper()
            )
        ).all()
    else:
        # For non-exact search, we prioritize:
        # 1. Exact case-insensitive match
        # 2. Names starting with the query
        # 3. Names containing the query
        
        q_lower = query.lower()
        
        # We use or_ and LIKE for broader coverage
        results = query_obj.filter(
            or_(
                Hashtag.name.like(f"%{query}%"),
                Hashtag.name.like(f"%{q_lower}%")
            )
        ).order_by(
            # Sorting logic: 
            # - Exact matches come first (regardless of case)
            # - Then matches starting with the query
            # - Then other matches
            case(
                (Hashtag.name == query, 0),
                (Hashtag.name == q_lower, 0),
                (Hashtag.name.like(f"{query}%"), 1),
                (Hashtag.name.like(f"{q_lower}%"), 1),
                else_=2
            ),
            # Secondary sort by popularity
            sql_func.count(tweet_hashtag_association.c.tweet_id).desc()
        ).limit(50).all()

    return [
        {
            'id': r[0],
            'name': r[1],
            'created_at': r[2],
            'tweet_count': r[3]
        }
        for r in results
    ]


def get_tweet(db: Session, tweet_id: int) -> Optional[Tweet]:
    """Get tweet by ID."""
    return db.query(Tweet).filter(Tweet.id == tweet_id).first()


def get_tweets(db: Session, skip: int = 0, limit: int = 100) -> List[Tweet]:
    """Get all tweets with pagination, ordered by latest first."""
    return db.query(Tweet).order_by(Tweet.created_at.desc()).offset(skip).limit(limit).all()


def extract_hashtags(content: str) -> List[str]:
    """Extract hashtags from tweet content."""
    # Find all words starting with #
    hashtags = re.findall(r'#(\w+)', content)
    return list(set(hashtags))  # Remove duplicates


def create_tweet(db: Session, tweet: TweetCreate) -> Tweet:
    """
    Create a new tweet and automatically create/associate hashtags.

    This function:
    1. Creates the tweet
    2. Extracts hashtags from content
    3. Creates new hashtags if they don't exist
    4. Associates hashtags with the tweet
    5. Adds random realistic likes and retweets
    """
    # Create the tweet with random likes and retweets
    db_tweet = Tweet(
        content=tweet.content,
        author_id=tweet.author_id,
        likes_count=random.randint(0, 500),
        retweets_count=random.randint(0, 200)
    )
    db.add(db_tweet)
    db.flush()  # Flush to get the tweet ID without committing

    # Extract and process hashtags
    hashtag_names = extract_hashtags(tweet.content)
    for hashtag_name in hashtag_names:
        # Create or get hashtag
        hashtag = get_hashtag_by_name(db, hashtag_name)
        if not hashtag:
            hashtag = create_hashtag(db, hashtag_name)

        # Associate with tweet
        if hashtag not in db_tweet.hashtags:
            db_tweet.hashtags.append(hashtag)
            # Optimization: Update the hashtag's latest_tweet_id
            hashtag.latest_tweet_id = db_tweet.id

    db.commit()
    db.refresh(db_tweet)
    return db_tweet


def inject_hashtags_to_user_tweets(db: Session, user_id: int, hashtags: List[str], percentage: int) -> int:
    """
    Randomly inject a list of hashtags into a percentage of a user's tweets.
    Returns the number of tweets updated.
    """
    # Get all tweets by user
    user_tweets = db.query(Tweet).filter(Tweet.author_id == user_id).all()
    if not user_tweets:
        return 0
    
    # Calculate how many to update
    num_to_update = max(1, int(len(user_tweets) * (percentage / 100.0)))
    tweets_to_update = random.sample(user_tweets, min(num_to_update, len(user_tweets)))
    
    hashtag_str = " " + " ".join([f"#{h.strip().lstrip('#')}" for h in hashtags])
    
    updated_count = 0
    for tweet in tweets_to_update:
        # Append hashtags to content
        tweet.content += hashtag_str
        
        # Extract and associate hashtags (standard Spyfind logic)
        hashtag_names = extract_hashtags(tweet.content)
        for hashtag_name in hashtag_names:
            hashtag_obj = get_hashtag_by_name(db, hashtag_name)
            if not hashtag_obj:
                hashtag_obj = create_hashtag(db, hashtag_name)
            
            if hashtag_obj not in tweet.hashtags:
                tweet.hashtags.append(hashtag_obj)
        
        updated_count += 1
    
    db.commit()
    return updated_count


def like_tweet(db: Session, tweet_id: int) -> Optional[Tweet]:
    """Increment like count for a tweet."""
    tweet = get_tweet(db, tweet_id)
    if tweet:
        tweet.likes_count += 1
        db.commit()
        db.refresh(tweet)
    return tweet


def get_tweets_by_hashtag_paginated(db: Session, hashtag_id: int, skip: int = 0, limit: int = 20) -> List[Tweet]:
    """Get tweets for a specific hashtag with pagination, ordered by latest first."""
    return db.query(Tweet).join(Tweet.hashtags).filter(Hashtag.id == hashtag_id).order_by(Tweet.created_at.desc()).offset(skip).limit(limit).all()


def count_tweets_by_hashtag(db: Session, hashtag_id: int) -> int:
    """Count tweets for a specific hashtag."""
    return db.query(Tweet).join(Tweet.hashtags).filter(Hashtag.id == hashtag_id).count()


def get_tweets_by_hashtag(db: Session, hashtag_id: int) -> List[Tweet]:
    """Get all tweets for a specific hashtag."""
    hashtag = get_hashtag(db, hashtag_id)
    if not hashtag:
        return []
    return hashtag.tweets


def get_top_hashtags_by_tweets(db: Session, limit: int = 10) -> List[dict]:
    """Get hashtags sorted by number of tweets (most tweets first)."""
    from sqlalchemy import func as sql_func
    
    # Still use the association table for popularity, but it's now faster
    results = db.query(
        Hashtag.id,
        Hashtag.name,
        Hashtag.created_at,
        sql_func.count(tweet_hashtag_association.c.tweet_id).label('tweet_count')
    ).outerjoin(
        tweet_hashtag_association, Hashtag.id == tweet_hashtag_association.c.hashtag_id
    ).group_by(
        Hashtag.id, Hashtag.name, Hashtag.created_at
    ).order_by(
        sql_func.count(tweet_hashtag_association.c.tweet_id).desc()
    ).limit(limit).all()

    return [
        {
            'id': r[0],
            'name': r[1],
            'created_at': r[2],
            'tweet_count': r[3]
        }
        for r in results
    ]


def get_top_hashtags_by_date(db: Session, limit: int = 10) -> List[dict]:
    """Get hashtags sorted by the most recent tweet that used them (optimized)."""
    from sqlalchemy import func as sql_func
    
    # Use the optimized latest_tweet_id column instead of complex joins
    results = db.query(
        Hashtag.id,
        Hashtag.name,
        Hashtag.created_at,
        sql_func.count(tweet_hashtag_association.c.tweet_id).label('tweet_count')
    ).outerjoin(
        tweet_hashtag_association, Hashtag.id == tweet_hashtag_association.c.hashtag_id
    ).group_by(
        Hashtag.id, Hashtag.name, Hashtag.created_at, Hashtag.latest_tweet_id
    ).order_by(
        Hashtag.latest_tweet_id.desc()
    ).limit(limit).all()

    return [
        {
            'id': r[0],
            'name': r[1],
            'created_at': r[2],
            'tweet_count': r[3]
        }
        for r in results
    ]


# ============================================================================
# REPOST OPERATIONS
# ============================================================================

def create_repost(db: Session, repost: RepostCreate) -> Repost:
    """
    Create a repost and update related counts.
    Increments the original tweet's retweets_count and the user's posts_count.
    """
    # Create the repost
    db_repost = Repost(
        user_id=repost.user_id,
        original_tweet_id=repost.original_tweet_id
    )
    db.add(db_repost)

    # Update tweet retweets count
    tweet = get_tweet(db, repost.original_tweet_id)
    if tweet:
        tweet.retweets_count += 1

    # Update user's posts count (reposts count as posts)
    user = get_user(db, repost.user_id)
    if user:
        user.posts_count += 1

    db.commit()
    db.refresh(db_repost)
    return db_repost


def get_repost(db: Session, repost_id: int) -> Optional[Repost]:
    """Get repost by ID."""
    return db.query(Repost).filter(Repost.id == repost_id).first()


def get_reposts_by_user(db: Session, user_id: int) -> List[Repost]:
    """Get all reposts by a specific user."""
    return db.query(Repost).filter(Repost.user_id == user_id).all()


def get_reposts_by_tweet(db: Session, tweet_id: int) -> List[Repost]:
    """Get all reposts of a specific tweet."""
    return db.query(Repost).filter(Repost.original_tweet_id == tweet_id).all()


# ============================================================================
# COMMENT OPERATIONS
# ============================================================================

def create_comment(db: Session, comment: CommentCreate) -> Comment:
    """
    Create a comment on a tweet and increment the tweet's comments_count.
    """
    db_comment = Comment(
        content=comment.content,
        tweet_id=comment.tweet_id,
        user_id=comment.user_id
    )
    db.add(db_comment)

    # Update tweet's comments count
    tweet = get_tweet(db, comment.tweet_id)
    if tweet:
        tweet.comments_count += 1

    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    """Get comment by ID."""
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_tweet(db: Session, tweet_id: int) -> List[Comment]:
    """Get all comments for a specific tweet."""
    return db.query(Comment).filter(Comment.tweet_id == tweet_id).order_by(Comment.created_at.desc()).all()


def get_comments_by_user(db: Session, user_id: int) -> List[Comment]:
    """Get all comments by a specific user."""
    return db.query(Comment).filter(Comment.user_id == user_id).all()
