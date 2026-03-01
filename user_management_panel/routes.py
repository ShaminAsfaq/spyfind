"""User Management Panel Routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.schemas import UserResponse, UserCreate
from app import crud
from app.models import User

router = APIRouter(prefix="/admin/users", tags=["user-management"])

class HashtagInjectionRequest(BaseModel):
    user_id: int
    hashtags: str
    percentage: int = 20


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and search.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **search**: Search by username or display_name
    """
    if search:
        users = db.query(User).filter(
            (User.username.ilike(f"%{search}%")) |
            (User.display_name.ilike(f"%{search}%"))
        ).offset(skip).limit(limit).all()
    else:
        users = crud.get_users(db, skip=skip, limit=limit)

    # Ensure None values are converted to 0 for counts
    for user in users:
        user.followers_count = user.followers_count or 0
        user.following_count = user.following_count or 0
        user.posts_count = user.posts_count or 0
        user.likes_count = user.likes_count or 0
        user.listed_count = user.listed_count or 0
        user.retweets_count = user.retweets_count or 0

    return users


@router.get("/count")
def get_users_count(db: Session = Depends(get_db)):
    """Get total count of users."""
    count = db.query(User).count()
    return {"total": count}


@router.get("/search", response_model=List[UserResponse])
def search_users_for_hashtag(query: str = Query(None), db: Session = Depends(get_db)):
    """Search users for the hashtag injection autocomplete feature."""
    if not query or len(query) < 2:
        return []
    
    users = db.query(User).filter(
        (User.username.ilike(f"%{query}%")) |
        (User.display_name.ilike(f"%{query}%"))
    ).limit(10).all()
    
    # Ensure None values are converted to appropriate defaults
    results = []
    for user in users:
        # Pydantic validation will fail if username/display_name is None
        if not user.username or not user.display_name:
            continue
            
        user.followers_count = user.followers_count or 0
        user.following_count = user.following_count or 0
        user.posts_count = user.posts_count or 0
        user.likes_count = user.likes_count or 0
        user.listed_count = user.listed_count or 0
        user.retweets_count = user.retweets_count or 0
        results.append(user)
        
    return results


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if username already exists
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    return crud.create_user(db, user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    """Update an existing user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if new username conflicts with another user
    if user_data.username != user.username:
        existing_user = crud.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

    # Update user fields
    user.username = user_data.username
    user.display_name = user_data.display_name
    user.bio = user_data.bio or ""
    user.location = user_data.location or ""
    user.url = user_data.url or ""
    user.followers_count = user_data.followers_count or 0
    user.following_count = user_data.following_count or 0
    user.posts_count = user_data.posts_count or 0
    user.likes_count = user_data.likes_count or 0
    user.listed_count = user_data.listed_count or 0
    user.retweets_count = user_data.retweets_count or 0
    user.profile_color = user_data.profile_color or "#1da1f2"
    user.banner_color = user_data.banner_color or "#ffffff"
    user.profile_image_url = user_data.profile_image_url
    user.profile_banner_url = user_data.profile_banner_url

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully", "user_id": user_id}


@router.post("/inject")
def inject_hashtags(
    request: HashtagInjectionRequest,
    db: Session = Depends(get_db)
):
    """
    Randomly inject hashtags into a percentage of a user's tweets.
    Returns the number of updated tweets.
    """
    hashtag_list = [h.strip() for h in request.hashtags.split(',') if h.strip()]
    if not hashtag_list:
        raise HTTPException(status_code=400, detail="No hashtags provided")
    
    # Verify user
    user = crud.get_user(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.percentage < 1 or request.percentage > 100:
        raise HTTPException(status_code=400, detail="Percentage must be between 1 and 100")
        
    updated_count = crud.inject_hashtags_to_user_tweets(db, request.user_id, hashtag_list, request.percentage)
    return {"message": f"Successfully updated {updated_count} tweets with hashtags", "updated_count": updated_count}
