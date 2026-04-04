"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user schema."""
    username: Optional[str] = ""
    display_name: Optional[str] = ""
    bio: Optional[str] = ""
    location: Optional[str] = ""
    url: Optional[str] = ""
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0
    posts_count: Optional[int] = 0
    likes_count: Optional[int] = 0
    listed_count: Optional[int] = 0
    retweets_count: Optional[int] = 0
    profile_color: Optional[str] = "#1da1f2"
    banner_color: Optional[str] = "#ffffff"
    profile_image_url: Optional[str] = None
    profile_banner_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class BotDetectionResponse(BaseModel):
    """Schema for bot detection status."""
    is_bot: bool
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: Optional[datetime] = None
    bot_status: Optional[BotDetectionResponse] = None

    class Config:
        from_attributes = True


class HashtagBase(BaseModel):
    """Base hashtag schema."""
    name: str


class HashtagCreate(HashtagBase):
    """Schema for creating a hashtag."""
    pass


class HashtagResponse(HashtagBase):
    """Schema for hashtag response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TweetBase(BaseModel):
    """Base tweet schema."""
    content: str
    author_id: int
    likes_count: int = 0
    retweets_count: int = 0
    comments_count: int = 0


class TweetCreate(BaseModel):
    """Schema for creating a tweet with optional hashtags."""
    content: str
    author_id: int


class TweetResponse(TweetBase):
    """Schema for tweet response with relationships."""
    id: int
    created_at: datetime
    author: UserResponse
    hashtags: List[HashtagResponse]

    class Config:
        from_attributes = True


class HashtagDetailResponse(HashtagResponse):
    """Schema for detailed hashtag response with tweets."""
    tweets: List[TweetResponse]

    class Config:
        from_attributes = True


class HashtagSummaryResponse(HashtagResponse):
    """Schema for hashtag response with tweet count instead of list."""
    tweet_count: int

    class Config:
        from_attributes = True


class TweetListResponse(BaseModel):
    """Schema for paginated tweet list."""
    tweets: List[TweetResponse]
    total: int
    skip: int
    limit: int


class RepostCreate(BaseModel):
    """Schema for creating a repost."""
    user_id: int
    original_tweet_id: int


class RepostResponse(BaseModel):
    """Schema for repost response."""
    id: int
    user_id: int
    original_tweet_id: int
    created_at: datetime
    user: UserResponse
    original_tweet: TweetResponse

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """Schema for creating a comment."""
    content: str
    tweet_id: int
    user_id: int


class CommentResponse(BaseModel):
    """Schema for comment response."""
    id: int
    content: str
    tweet_id: int
    user_id: int
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True


class DemonstrationRequest(BaseModel):
    """Schema for demonstration request."""
    num_bots: int
    num_posts: int
    hashtags: str


class HashtagAnalysisUser(BaseModel):
    """Schema for a user in hashtag analysis."""
    id: int
    username: str
    display_name: str
    prediction: str
    is_bot: bool
    confidence: Optional[int] = None


class HashtagAnalysisResponse(BaseModel):
    """Schema for detailed hashtag analysis report."""
    hashtag_id: int
    hashtag_name: str
    total_tweets: int
    total_users: int
    bot_count: int
    human_count: int
    bot_percentage: float
    users: List[HashtagAnalysisUser]
