"""Seed script to populate sample data into Spyfind database."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import User, Tweet, Hashtag
from app.crud import create_user, create_tweet
from app.schemas import UserCreate, TweetCreate


def seed_database():
    """Populate database with sample data."""
    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Check if data already exists
        user_count = db.query(User).count()
        if user_count > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("🌱 Seeding database with sample data...")

        # ===== CREATE SAMPLE USERS =====
        users_data = [
            {
                "username": "alice_dev",
                "display_name": "Alice Developer",
                "bio": "Python enthusiast | Bot detection researcher",
                "location": "San Francisco, CA",
                "followers_count": 1250,
                "following_count": 340
            },
            {
                "username": "bot_hunter",
                "display_name": "Bot Hunter",
                "bio": "Detecting fake accounts since 2020",
                "location": "New York, NY",
                "followers_count": 5840,
                "following_count": 120
            },
            {
                "username": "security_researcher",
                "display_name": "Security Researcher",
                "bio": "Cybersecurity | Automation | Testing",
                "location": "London, UK",
                "followers_count": 3200,
                "following_count": 450
            },
            {
                "username": "spam_detector",
                "display_name": "Spam Detector Bot",
                "bio": "Automated spam detection system",
                "location": "Everywhere",
                "followers_count": 8900,
                "following_count": 0
            },
            {
                "username": "test_account",
                "display_name": "Test Account",
                "bio": "Testing purposes only",
                "location": "Test City",
                "followers_count": 100,
                "following_count": 50
            },
            {
                "username": "suspicious_user",
                "display_name": "Suspicious Activity",
                "bio": "Posting frequently from multiple IPs",
                "location": "Unknown",
                "followers_count": 15,
                "following_count": 5000
            }
        ]

        users = []
        for user_data in users_data:
            user = create_user(db, UserCreate(**user_data))
            users.append(user)
            print(f"  ✓ Created user: @{user.username}")

        # ===== CREATE SAMPLE TWEETS =====
        tweets_data = [
            {
                "author_id": users[0].id,
                "content": "Just released a new bot detection model! Check out #botdetection #python #security on GitHub"
            },
            {
                "author_id": users[0].id,
                "content": "Working on improving the #botdetection algorithms. #testing #ml"
            },
            {
                "author_id": users[1].id,
                "content": "Found 3 suspicious accounts using #botdetection techniques. #security #analysis"
            },
            {
                "author_id": users[1].id,
                "content": "#botdetection is becoming crucial for platform safety. We need better tools! #security"
            },
            {
                "author_id": users[2].id,
                "content": "New research paper on automated #botdetection using machine learning #ml #research"
            },
            {
                "author_id": users[2].id,
                "content": "Testing our #botdetection system with large-scale data. Results are promising! #testing #datascience"
            },
            {
                "author_id": users[3].id,
                "content": "Spam alert: Detected 42 new bot accounts today #botdetection #spam #security"
            },
            {
                "author_id": users[3].id,
                "content": "Daily report: 156 suspicious activities logged #botdetection #monitoring"
            },
            {
                "author_id": users[4].id,
                "content": "Testing posting behavior for #testing #botdetection experiments"
            },
            {
                "author_id": users[4].id,
                "content": "Multiple tweets in rapid succession #testing #botdetection #automation"
            },
            {
                "author_id": users[5].id,
                "content": "Follow me and check out my profile! Click here for more! #botdetection #spam #testing"
            },
            {
                "author_id": users[5].id,
                "content": "Urgent: #botdetection bypass methods revealed! #spam #suspicious"
            },
            {
                "author_id": users[0].id,
                "content": "Exciting updates coming to our #botdetection platform this quarter #python #development"
            },
            {
                "author_id": users[1].id,
                "content": "Community discussion: What features should #botdetection tools have? #security #feedback"
            },
        ]

        for tweet_data in tweets_data:
            tweet = create_tweet(db, TweetCreate(**tweet_data))
            hashtags_str = ", ".join([f"#{h.name}" for h in tweet.hashtags])
            print(f"  ✓ Created tweet by @{tweet.author.username} with hashtags: {hashtags_str}")

        # ===== SUMMARY =====
        final_user_count = db.query(User).count()
        final_tweet_count = db.query(Tweet).count()
        final_hashtag_count = db.query(Hashtag).count()

        print("\n✅ Database seeding complete!")
        print(f"   Users: {final_user_count}")
        print(f"   Tweets: {final_tweet_count}")
        print(f"   Hashtags: {final_hashtag_count}")
        print("\n💡 Start the server with: python app/main.py")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
