"""
Migration script to update database schema and populate with realistic data.

This script:
1. Recreates database tables with new schema
2. Populates existing users with realistic random data for new fields
3. Adds sample reposts and comments
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models import User, Tweet, Hashtag, Repost, Comment


def generate_random_color_palette():
    """Generate color palettes for profiles and banners."""
    profile_colors = [
        "#1da1f2", "#e74c3c", "#3498db", "#9b59b6", "#2ecc71",
        "#f39c12", "#34495e", "#e67e22", "#1abc9c", "#d35400",
        "#c0392b", "#8e44ad", "#27ae60", "#2980b9", "#16a085"
    ]
    banner_colors = [
        "#ffffff", "#f0f0f0", "#e8f5ff", "#fff3e0", "#f3e5f5",
        "#e8f8f5", "#fce4ec", "#e0f2f1", "#fef5e7", "#eaecee"
    ]
    return profile_colors, banner_colors


def update_existing_users(db):
    """Update existing users with new fields and realistic data."""
    print("Updating existing users with new profile data...")

    profile_colors, banner_colors = generate_random_color_palette()
    users = db.query(User).all()

    for user in users:
        # Update colors
        user.profile_color = random.choice(profile_colors)
        user.banner_color = random.choice(banner_colors)

        # Generate realistic stats if not already set
        if user.followers_count == 0:
            followers = random.choices(
                [random.randint(10, 500), random.randint(500, 2000),
                 random.randint(2000, 10000), random.randint(10000, 50000)],
                weights=[70, 20, 8, 2]
            )[0]
            user.followers_count = followers

        if user.following_count == 0:
            user.following_count = random.randint(50, min(2000, user.followers_count + 500))

        # Count actual tweets for this user
        tweet_count = db.query(Tweet).filter(Tweet.author_id == user.id).count()
        user.posts_count = tweet_count

        # Calculate total likes received on all tweets
        tweets = db.query(Tweet).filter(Tweet.author_id == user.id).all()
        total_likes = sum(tweet.likes_count for tweet in tweets)
        user.likes_count = total_likes

        # Listed count - fraction of followers
        user.listed_count = random.randint(0, max(1, user.followers_count // 10))

        # URL field - some users have URLs, some don't
        if random.random() < 0.3:  # 30% of users have URLs
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
    for tweet in tweets[:20]:  # Add comments to first 20 tweets
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
    for tweet in tweets[:15]:  # Add reposts for first 15 tweets
        num_reposts = random.randint(0, 3)
        for _ in range(num_reposts):
            reposter = random.choice([u for u in users if u.id != tweet.author_id])

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
    """Main migration function."""
    print("=" * 60)
    print("Starting database migration and data population...")
    print("=" * 60)

    # Recreate all tables with new schema
    print("\nRecreating database tables with new schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database schema updated successfully!")

    db = SessionLocal()
    try:
        # Note: Since we dropped all tables, we need to re-import existing data
        # For now, we'll just create the schema
        # In production, you'd want to use proper migrations with Alembic
        print("\nDatabase is now ready with the new schema.")
        print("You can now add new users with the enhanced profile features!")

        # If you want to test with sample data, uncomment these:
        # update_existing_users(db)
        # add_sample_comments(db)
        # add_sample_reposts(db)

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("Migration completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
