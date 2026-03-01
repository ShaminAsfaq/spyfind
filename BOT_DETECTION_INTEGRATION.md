# Bot Detection Integration Guide

This guide explains how to integrate external bot-detection modules with Spyfind.

## Overview

Spyfind is designed with extensibility in mind. The API endpoints provide all necessary data for external bot-detection analysis systems.

## Available Data Sources

### 1. User Analysis
Get comprehensive user metadata:

```bash
GET /api/users/{user_id}
```

**Response includes:**
- `username`: Unique identifier
- `display_name`: Public display name
- `bio`: User biography (sentiment analysis candidate)
- `location`: Reported location
- `followers_count`: Social proof metric
- `following_count`: Following behavior metric
- `created_at`: Account age (important for bot detection)

**Use Cases:**
- Detect newly created accounts posting spam
- Analyze follower/following ratios (suspicious if following >> followers)
- Extract bio keywords for spam detection

### 2. Tweet Analysis
Get detailed tweet information with full context:

```bash
GET /api/tweets
GET /api/tweets/{tweet_id}
```

**Response includes:**
- `content`: Tweet text for NLP analysis
- `author_id`: Link to user profile
- `created_at`: Tweet timestamp (detect posting patterns)
- `likes_count`: Engagement metrics
- `hashtags`: Array of associated hashtags
- `author`: Full user object

**Use Cases:**
- Analyze posting frequency (time between tweets)
- Detect spam patterns in content
- Analyze hashtag stuffing (too many hashtags)
- Perform sentiment analysis
- Detect URL shorteners or suspicious links

### 3. Hashtag Intelligence
Track hashtag usage patterns:

```bash
GET /api/hashtags/search/{query}
GET /api/hashtags/{hashtag_id}
```

**Response includes:**
- Hashtag name and creation date
- All tweets using that hashtag
- Authors of those tweets
- Timestamp of first mention

**Use Cases:**
- Detect trending spam hashtags
- Identify coordinated campaigns (multiple accounts using specific hashtags)
- Track hashtag evolution and adoption patterns
- Detect hashtag hijacking

## Integration Patterns

### Pattern 1: Real-Time Bot Scoring

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
import requests

router = APIRouter()

def calculate_bot_score(user_id: int, db: Session):
    """
    Analyze a user for bot-like behavior.
    Returns a score from 0 (human) to 1 (bot).
    """
    user = crud.get_user(db, user_id)
    tweets = db.query(Tweet).filter(Tweet.author_id == user_id).all()

    score = 0.0
    reasons = []

    # Factor 1: Account Age (0-0.3 points)
    account_age_days = (datetime.now() - user.created_at).days
    if account_age_days < 7:
        score += 0.3
        reasons.append("Very new account (< 7 days)")
    elif account_age_days < 30:
        score += 0.15
        reasons.append("New account (< 30 days)")

    # Factor 2: Follower/Following Ratio (0-0.25 points)
    if user.followers_count == 0 and user.following_count > 100:
        score += 0.25
        reasons.append("Following many but no followers")
    elif user.following_count > 0:
        ratio = user.followers_count / max(user.following_count, 1)
        if ratio < 0.5:
            score += 0.15
            reasons.append("Low follower/following ratio")

    # Factor 3: Posting Frequency (0-0.2 points)
    if len(tweets) > 50:
        # Check if posted in last 24 hours
        recent_tweets = [t for t in tweets if (datetime.now() - t.created_at).days < 1]
        if len(recent_tweets) > 20:
            score += 0.2
            reasons.append("High posting frequency (20+ tweets/day)")

    # Factor 4: Bio Analysis (0-0.15 points)
    suspicious_bio_keywords = ["follow", "followers", "click here", "link in bio"]
    bio_lower = user.bio.lower() if user.bio else ""
    if any(keyword in bio_lower for keyword in suspicious_bio_keywords):
        score += 0.15
        reasons.append("Suspicious keywords in bio")

    # Factor 5: Hashtag Stuffing (0-0.1 points)
    avg_hashtags = sum(len(t.hashtags) for t in tweets) / max(len(tweets), 1)
    if avg_hashtags > 5:
        score += 0.1
        reasons.append(f"Excessive hashtags (avg {avg_hashtags:.1f} per tweet)")

    return {
        "user_id": user_id,
        "username": user.username,
        "bot_score": min(score, 1.0),  # Cap at 1.0
        "classification": "bot" if score > 0.7 else "suspicious" if score > 0.4 else "human",
        "factors": reasons,
        "tweet_count": len(tweets),
        "account_age_days": account_age_days
    }

@router.get("/api/analytics/bot-score/{user_id}")
def get_bot_score(user_id: int, db: Session = Depends(get_db)):
    """Analyze user for bot-like behavior."""
    return calculate_bot_score(user_id, db)
```

### Pattern 2: Bulk Analysis Report

```python
@router.get("/api/analytics/report/suspicious-accounts")
def get_suspicious_accounts(threshold: float = 0.5, db: Session = Depends(get_db)):
    """
    Get all users with bot score above threshold.
    Useful for generating security reports.
    """
    all_users = crud.get_users(db, skip=0, limit=10000)

    suspicious = []
    for user in all_users:
        result = calculate_bot_score(user.id, db)
        if result["bot_score"] >= threshold:
            suspicious.append(result)

    return {
        "timestamp": datetime.now(),
        "threshold": threshold,
        "suspicious_count": len(suspicious),
        "accounts": sorted(suspicious, key=lambda x: x["bot_score"], reverse=True)
    }
```

### Pattern 3: Content Analysis

```python
import re

def analyze_tweet_content(tweet_id: int, db: Session):
    """
    Analyze tweet content for spam/bot indicators.
    """
    tweet = crud.get_tweet(db, tweet_id)
    content = tweet.content

    analysis = {
        "tweet_id": tweet_id,
        "author_id": tweet.author_id,
        "spam_indicators": [],
        "spam_score": 0.0
    }

    # Check for URL shorteners
    shortener_pattern = r'(bit\.ly|tinyurl|t\.co|ow\.ly|goo\.gl)'
    if re.search(shortener_pattern, content):
        analysis["spam_indicators"].append("URL shortener detected")
        analysis["spam_score"] += 0.2

    # Check for excessive mentions
    mention_count = len(re.findall(r'@\w+', content))
    if mention_count > 5:
        analysis["spam_indicators"].append(f"Excessive mentions: {mention_count}")
        analysis["spam_score"] += 0.15

    # Check for all caps (usually spam)
    caps_percentage = sum(1 for c in content if c.isupper()) / len(content)
    if caps_percentage > 0.5:
        analysis["spam_indicators"].append("Excessive capitalization")
        analysis["spam_score"] += 0.1

    # Check for repeated words
    words = content.lower().split()
    if len(words) > 0:
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        if max(word_freq.values()) / len(words) > 0.3:
            analysis["spam_indicators"].append("Word repetition detected")
            analysis["spam_score"] += 0.15

    return analysis

@router.get("/api/analytics/tweet-analysis/{tweet_id}")
def analyze_tweet(tweet_id: int, db: Session = Depends(get_db)):
    """Analyze a specific tweet for spam indicators."""
    return analyze_tweet_content(tweet_id, db)
```

### Pattern 4: Coordinated Behavior Detection

```python
@router.get("/api/analytics/coordinated-campaigns")
def detect_coordinated_behavior(db: Session = Depends(get_db)):
    """
    Detect potential coordinated bot campaigns
    (e.g., multiple accounts tweeting same hashtag in short time).
    """
    all_tweets = crud.get_tweets(db, skip=0, limit=10000)
    hashtag_activity = {}

    # Track hashtag usage patterns
    for tweet in all_tweets:
        for hashtag in tweet.hashtags:
            if hashtag.name not in hashtag_activity:
                hashtag_activity[hashtag.name] = []
            hashtag_activity[hashtag.name].append({
                "user_id": tweet.author_id,
                "timestamp": tweet.created_at
            })

    # Detect suspicious patterns
    suspicious_campaigns = []
    for hashtag_name, activity in hashtag_activity.items():
        if len(activity) >= 5:  # 5+ tweets with same hashtag
            # Check if from different users
            unique_users = len(set(a["user_id"] for a in activity))

            if unique_users >= 3:  # 3+ different users
                # Check if in short time window
                timestamps = sorted([a["timestamp"] for a in activity])
                time_span = (timestamps[-1] - timestamps[0]).total_seconds()

                if time_span < 3600:  # Within 1 hour
                    suspicious_campaigns.append({
                        "hashtag": hashtag_name,
                        "user_count": unique_users,
                        "tweet_count": len(activity),
                        "time_span_minutes": time_span / 60,
                        "score": 0.8  # High confidence coordinated activity
                    })

    return {
        "timestamp": datetime.now(),
        "potential_campaigns": suspicious_campaigns,
        "campaign_count": len(suspicious_campaigns)
    }
```

## Data Export for External Analysis

### Export All Data as JSON

```bash
# Get all users
curl http://localhost:8000/api/users?skip=0&limit=10000 > users.json

# Get all tweets
curl http://localhost:8000/api/tweets?skip=0&limit=10000 > tweets.json

# Get all hashtags
curl http://localhost:8000/api/hashtags?skip=0&limit=10000 > hashtags.json
```

### Process Exported Data

```python
import json
import pandas as pd

# Load data
with open('tweets.json') as f:
    tweets = json.load(f)

with open('users.json') as f:
    users = json.load(f)

# Create DataFrames for analysis
tweets_df = pd.DataFrame(tweets)
users_df = pd.DataFrame(users)

# Example: Find accounts with unusual patterns
new_accounts = users_df[
    (pd.to_datetime(users_df['created_at']).dt.date == today) &
    (users_df['followers_count'] < 10) &
    (users_df['following_count'] > 100)
]

print(f"Found {len(new_accounts)} suspicious new accounts")
```

## Machine Learning Integration

### Example: Using Scikit-learn for Bot Classification

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np

def prepare_features(user_id: int, db: Session):
    """Extract features for ML model."""
    user = crud.get_user(db, user_id)
    tweets = db.query(Tweet).filter(Tweet.author_id == user_id).all()

    account_age = (datetime.now() - user.created_at).days
    follower_ratio = user.followers_count / max(user.following_count, 1)
    avg_likes = np.mean([t.likes_count for t in tweets]) if tweets else 0
    avg_hashtags = np.mean([len(t.hashtags) for t in tweets]) if tweets else 0

    return np.array([
        account_age,
        user.followers_count,
        user.following_count,
        follower_ratio,
        len(tweets),
        avg_likes,
        avg_hashtags
    ]).reshape(1, -1)

# Train model (example)
# X_train = [prepare_features(uid, db) for uid in user_ids]
# y_train = [ground_truth_labels]  # 1 = bot, 0 = human
# model = RandomForestClassifier()
# model.fit(X_train, y_train)

@router.get("/api/analytics/ml-bot-score/{user_id}")
def get_ml_bot_score(user_id: int, db: Session = Depends(get_db)):
    """ML-based bot detection score."""
    features = prepare_features(user_id, db)
    # probability = model.predict_proba(features)[0][1]
    # For demo, return mock prediction
    return {
        "user_id": user_id,
        "ml_bot_probability": 0.42,
        "features_used": [
            "account_age_days",
            "followers_count",
            "following_count",
            "follower_ratio",
            "tweet_count",
            "avg_likes",
            "avg_hashtags"
        ]
    }
```

## Testing Your Bot Detection

```bash
# 1. Create test data
curl -X POST http://localhost:8000/api/tweets \
  -H "Content-Type: application/json" \
  -d '{"author_id": 6, "content": "#botdetection #test #spam #spam #spam"}'

# 2. Analyze the suspicious user
curl http://localhost:8000/api/analytics/bot-score/6

# 3. Check content analysis
curl http://localhost:8000/api/analytics/tweet-analysis/1

# 4. Generate report
curl http://localhost:8000/api/analytics/report/suspicious-accounts?threshold=0.5
```

## Best Practices

1. **Feature Engineering**: Combine multiple signals (age, posting patterns, content)
2. **Time-Based Analysis**: Track changes over time (accounts that suddenly change behavior)
3. **Network Analysis**: Analyze follow graphs and mention patterns
4. **Content Analysis**: Use NLP for spam detection and sentiment analysis
5. **Ground Truth**: Collect labeled data to train models
6. **Ensemble Methods**: Combine multiple detection approaches
7. **Rate Limiting**: Detect accounts posting at inhuman speeds
8. **Fingerprinting**: Detect reused device identifiers, IPs, etc.

## Future Extensions

- Add graph database for social network analysis
- Integrate ML models for real-time classification
- Add webhook support for external services
- Implement batch processing for large-scale analysis
- Add visualization dashboard for bot detection insights
