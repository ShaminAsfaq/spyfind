"""SQLAlchemy ORM Models for Spyfind."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for many-to-many relationship between tweets and hashtags
tweet_hashtag_association = Table(
    'tweet_hashtag',
    Base.metadata,
    Column('tweet_id', Integer, ForeignKey('tweets.id', ondelete='CASCADE')),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id', ondelete='CASCADE'))
)


class User(Base):
    """User model representing a Twitter/X user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    bio = Column(Text, default="")
    location = Column(String, default="")
    url = Column(String, default="")  # User's website/link
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)  # Total posts (tweets + reposts)
    likes_count = Column(Integer, default=0)  # Total likes received
    listed_count = Column(Integer, default=0)  # Number of lists user is on
    retweets_count = Column(Integer, default=0)  # Total retweets from this user
    profile_color = Column(String, default="#1da1f2")  # Hex color for profile image
    banner_color = Column(String, default="#ffffff")  # Hex color for banner
    profile_image_url = Column(String, nullable=True)
    profile_banner_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tweets = relationship("Tweet", back_populates="author", cascade="all, delete-orphan")
    reposts = relationship("Repost", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Hashtag(Base):
    """Hashtag model representing a searchable hashtag."""
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tweets = relationship(
        "Tweet",
        secondary=tweet_hashtag_association,
        back_populates="hashtags"
    )

    def __repr__(self):
        return f"<Hashtag(id={self.id}, name={self.name})>"


class Tweet(Base):
    """Tweet model representing a single tweet/post."""
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    likes_count = Column(Integer, default=0)
    retweets_count = Column(Integer, default=0)  # Number of times retweeted
    comments_count = Column(Integer, default=0)  # Number of comments

    # Relationships
    author = relationship("User", back_populates="tweets")
    hashtags = relationship(
        "Hashtag",
        secondary=tweet_hashtag_association,
        back_populates="tweets"
    )
    reposts = relationship("Repost", back_populates="original_tweet", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="tweet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tweet(id={self.id}, author_id={self.author_id})>"


class Repost(Base):
    """Repost model representing a user reposting someone else's tweet."""
    __tablename__ = "reposts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    original_tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reposts")
    original_tweet = relationship("Tweet", back_populates="reposts")

    def __repr__(self):
        return f"<Repost(id={self.id}, user_id={self.user_id}, tweet_id={self.original_tweet_id})>"


class Comment(Base):
    """Comment model representing a comment on a tweet."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tweet = relationship("Tweet", back_populates="comments")
    user = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, tweet_id={self.tweet_id}, user_id={self.user_id})>"
