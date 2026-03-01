"""
Update script to add new columns and populate existing data.

This script updates the database without dropping existing data by:
1. Adding new columns to existing tables
2. Populating existing users with realistic random data
3. Adding sample reposts and comments
"""
import sys
import os
import random
from datetime import datetime, timedelta
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models import User, Tweet, Repost, Comment


def add_new_columns(db):
    """Add new columns to existing tables."""
    print("Adding new columns to database tables...")

    try:
        # Add new columns to users table
        user_columns = [
            "ALTER TABLE users ADD COLUMN url TEXT DEFAULT ''",
            "ALTER TABLE users ADD COLUMN posts_count INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN likes_count INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN listed_count INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN profile_color TEXT DEFAULT '#1da1f2'",
            "ALTER TABLE users ADD COLUMN banner_color TEXT DEFAULT '#ffffff'"
        ]

        # Add new column to tweets table
        tweet_columns = [
            "ALTER TABLE tweets ADD COLUMN comments_count INTEGER DEFAULT 0"
        ]

        # Execute user column additions
        for column in user_columns:
            try:
                db.execute(text(column))
                db.commit()
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"Column already exists, skipping: {column.split('ADD COLUMN')[1].split()[0]}")
                else:
                    print(f"Error adding column: {e}")

        # Execute tweet column additions
        for column in tweet_columns:
            try:
                db.execute(text(column))
                db.commit()
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"Column already exists, skipping: {column.split('ADD COLUMN')[1].split()[0]}")
                else:
                    print(f"Error adding column: {e}")

        print("Columns added successfully!")

    except Exception as e:
        print(f"Error adding columns: {e}")
        db.rollback()


def create_new_tables(db):
    """Create reposts and comments tables if they don't exist."""
    print("Creating new tables (reposts, comments)...")

    try:
        # Create reposts table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS reposts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                original_tweet_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (original_tweet_id) REFERENCES tweets(id) ON DELETE CASCADE
            )
        """))

        # Create comments table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                tweet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tweet_id) REFERENCES tweets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        db.commit()
        print("New tables created successfully!")

    except Exception as e:
        print(f"Error creating tables: {e}")
        db.rollback()


def update_existing_users(db):
    """Update existing users with new fields and realistic data."""
    print("Updating existing users with new profile data...")

    profile_colors = [
        "#1da1f2", "#e74c3c", "#3498db", "#9b59b6", "#2ecc71",
        "#f39c12", "#34495e", "#e67e22", "#1abc9c", "#d35400",
        "#c0392b", "#8e44ad", "#27ae60", "#2980b9", "#16a085"
    ]
    banner_colors = [
        "#ffffff", "#f0f0f0", "#e8f5ff", "#fff3e0", "#f3e5f5",
        "#e8f8f5", "#fce4ec", "#e0f2f1", "#fef5e7", "#eaecee"
    ]

    users = db.query(User).all()

    for user in users:
        # Update colors
        user.profile_color = random.choice(profile_colors)
        user.banner_color = random.choice(banner_colors)

        # Generate realistic followers if currently 0 or not set properly
        if user.followers_count < 10:
            followers = random.choices(
                [random.randint(10, 500), random.randint(500, 2000),
                 random.randint(2000, 10000), random.randint(10000, 50000)],
                weights=[70, 20, 8, 2]
            )[0]
            user.followers_count = followers

        # Generate realistic following count
        if user.following_count < 10:
            user.following_count = random.randint(50, min(2000, user.followers_count + 500))

        # Count actual tweets for this user
        tweet_count = db.query(Tweet).filter(Tweet.author_id == user.id).count()
        user.posts_count = tweet_count if tweet_count > 0 else random.randint(100, 5000)

        # Calculate total likes received on all tweets
        tweets = db.query(Tweet).filter(Tweet.author_id == user.id).all()
        if tweets:
            total_likes = sum(tweet.likes_count for tweet in tweets)
            user.likes_count = total_likes
        else:
            user.likes_count = random.randint(user.posts_count // 2, user.posts_count * 50)

        # Listed count - fraction of followers
        user.listed_count = random.randint(0, max(1, user.followers_count // 10))

        # URL field - some users have URLs, some don't
        if not user.url and random.random() < 0.3:  # 30% of users have URLs
            domains = ["github.com", "linkedin.com", "example.com", "portfolio.io", "blog.com"]
            user.url = f"https://{random.choice(domains)}/{user.username}"

    db.commit()
    print(f"Updated {len(users)} users with new profile data")


def add_sample_comments(db):
    """Add sample comments to existing tweets."""
    print("Adding sample comments...")

    tweets = db.query(Tweet).all()
    users = db.query(User).all()

    if not tweets or not users:
        print("No tweets or users found. Skipping comments.")
        return

    comment_templates = [
        "Great point! I completely agree.",
        "This is really interesting, thanks for sharing!",
        "Could you elaborate more on this?",
        "Fantastic insight!",
        "I have a different perspective on this...",
        "This is exactly what I needed to read today.",
        "Couldn't agree more!",
        "Interesting take, but have you considered...?",
        "Thanks for bringing this to my attention.",
        "This deserves more visibility!",
        "Well said!",
        "I'm not sure I agree with this.",
        "Can you provide more context?",
        "This is gold!",
        "Amazing thread!"
    ]

    comments_created = 0
    for tweet in tweets[:min(20, len(tweets))]:  # Add comments to first 20 tweets
        num_comments = random.randint(0, 5)
        for _ in range(num_comments):
            commenter = random.choice(users)
            comment = Comment(
                content=random.choice(comment_templates),
                tweet_id=tweet.id,
                user_id=commenter.id,
                created_at=tweet.created_at + timedelta(minutes=random.randint(1, 1440))
            )
            db.add(comment)
            tweet.comments_count += 1
            comments_created += 1

    db.commit()
    print(f"Added {comments_created} sample comments")


def add_sample_reposts(db):
    """Add sample reposts for existing tweets."""
    print("Adding sample reposts...")

    tweets = db.query(Tweet).all()
    users = db.query(User).all()

    if not tweets or not users:
        print("No tweets or users found. Skipping reposts.")
        return

    reposts_created = 0
    for tweet in tweets[:min(15, len(tweets))]:  # Add reposts for first 15 tweets
        num_reposts = random.randint(0, 3)
        for _ in range(num_reposts):
            # Get users other than the author
            eligible_users = [u for u in users if u.id != tweet.author_id]
            if not eligible_users:
                continue

            reposter = random.choice(eligible_users)

            # Check if this user already reposted this tweet
            existing = db.query(Repost).filter(
                Repost.user_id == reposter.id,
                Repost.original_tweet_id == tweet.id
            ).first()

            if not existing:
                repost = Repost(
                    user_id=reposter.id,
                    original_tweet_id=tweet.id,
                    created_at=tweet.created_at + timedelta(hours=random.randint(1, 48))
                )
                db.add(repost)
                tweet.retweets_count += 1
                reposter.posts_count += 1
                reposts_created += 1

    db.commit()
    print(f"Added {reposts_created} sample reposts")


def main():
    """Main update function."""
    print("=" * 60)
    print("Starting database update and data population...")
    print("=" * 60)

    db = SessionLocal()
    try:
        # Step 1: Add new columns to existing tables
        add_new_columns(db)

        # Step 2: Create new tables (reposts, comments)
        create_new_tables(db)

        # Step 3: Update existing users with new data
        update_existing_users(db)

        # Step 4: Add sample comments
        add_sample_comments(db)

        # Step 5: Add sample reposts
        add_sample_reposts(db)

        print("\n" + "=" * 60)
        print("Database update completed successfully!")
        print("=" * 60)
        print("\nNew features added:")
        print("  - User profiles now have colors, URLs, and detailed stats")
        print("  - Comments and reposts functionality")
        print("  - All existing data preserved!")

    except Exception as e:
        print(f"\nError during update: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
