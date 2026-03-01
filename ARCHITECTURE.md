# Spyfind Architecture & Design

## Overview

Spyfind is a lightweight Twitter/X simulation designed specifically for testing and developing bot-detection systems. It follows clean architecture principles with clear separation between backend and frontend layers.

## Project Structure

```
spyfind/
├── app/                          # Backend application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # SQLAlchemy setup and session management
│   ├── models.py                # ORM models (User, Tweet, Hashtag)
│   ├── schemas.py               # Pydantic schemas for API validation
│   ├── crud.py                  # Database CRUD operations
│   └── routes.py                # API endpoint definitions
├── static/                       # Frontend files
│   └── index.html               # Single-page application UI
├── scripts/                      # Utility scripts
│   ├── __init__.py
│   └── seed.py                  # Database population script
├── venv/                         # Python virtual environment
├── requirements.txt             # Python dependencies
├── run.sh                        # Server launch script
├── README.md                     # Project documentation
├── ARCHITECTURE.md              # This file
└── spyfind.db                   # SQLite database (auto-generated)
```

## Database Design

### Models

#### User
- **id**: Integer, Primary Key
- **username**: String, Unique, Indexed (for @mentions)
- **display_name**: String (user's full name)
- **bio**: Text (optional user biography)
- **location**: String (optional location)
- **followers_count**: Integer (tracked statistic)
- **following_count**: Integer (tracked statistic)
- **created_at**: DateTime (account creation timestamp)

**Relationships:**
- One-to-Many with Tweet (User can have many tweets)

#### Tweet
- **id**: Integer, Primary Key
- **content**: Text (tweet message body)
- **author_id**: Integer, Foreign Key → User
- **created_at**: DateTime (tweet creation timestamp)
- **likes_count**: Integer (like counter)

**Relationships:**
- Many-to-One with User (Tweet belongs to one author)
- Many-to-Many with Hashtag (through `tweet_hashtag` association table)

#### Hashtag
- **id**: Integer, Primary Key
- **name**: String, Unique, Indexed (for search efficiency)
- **created_at**: DateTime (when hashtag was first created)

**Relationships:**
- Many-to-Many with Tweet (Hashtag can be in many tweets)

### Association Table
- **tweet_hashtag**: Junction table for many-to-many relationship
  - Columns: `tweet_id` (FK), `hashtag_id` (FK)
  - Features: CASCADE delete on both sides for data integrity

## Backend Architecture

### Layer: Data Access (crud.py)
**Responsibility:** Database operations and business logic

Key functions:
- `create_user()` - Create new users
- `create_tweet()` - Create tweets with automatic hashtag extraction and creation
- `create_hashtag()` - Create or retrieve hashtags (idempotent)
- `extract_hashtags()` - Parse tweet content for #hashtags using regex
- `search_hashtags()` - Case-insensitive hashtag search
- `get_user()`, `get_tweet()`, `get_hashtag()` - Retrieve by ID
- `like_tweet()` - Increment like counter

**Key Feature:** `create_tweet()` automatically:
1. Creates the tweet record
2. Extracts hashtags from content using regex pattern `#(\w+)`
3. Creates new hashtags if they don't exist (idempotent)
4. Associates hashtags with the tweet via many-to-many relationship

### Layer: API Routes (routes.py)
**Responsibility:** HTTP endpoint handlers and response formatting

#### Users Endpoints
- `GET /api/users` - List all users (paginated)
- `GET /api/users/{user_id}` - Get specific user
- `POST /api/users` - Create new user

#### Hashtags Endpoints
- `GET /api/hashtags` - List all hashtags (paginated)
- `GET /api/hashtags/{hashtag_id}` - Get hashtag with all its tweets
- `GET /api/hashtags/search/{query}` - Search hashtags by name (case-insensitive)

#### Tweets Endpoints
- `GET /api/tweets` - List all tweets (paginated)
- `GET /api/tweets/{tweet_id}` - Get specific tweet
- `POST /api/tweets` - Create new tweet (auto-hashtag extraction)
- `POST /api/tweets/{tweet_id}/like` - Like a tweet

### Validation (schemas.py)
Using Pydantic for:
- Request validation (TweetCreate, UserCreate)
- Response serialization (TweetResponse, UserResponse)
- Type safety and documentation

## Frontend Architecture

### Technology Stack
- Vanilla JavaScript (no frameworks)
- HTML5 semantic markup
- CSS3 with Flexbox/Grid layouts
- RESTful API consumption

### Key Features

#### Search Interface
- Real-time hashtag search with autocomplete
- Dynamic result loading
- Tweet cards with author info
- Clickable hashtags that trigger searches

#### User Profiles
- Full user metadata display
- User statistics (followers, following)
- Account creation date
- All user tweets with timestamps

#### Tweet Creation
- Modal dialog for creating tweets
- User selection dropdown
- Hashtag auto-detection in UI
- Real-time hashtag linking

#### Interactive Elements
- Like functionality with counter update
- Clickable usernames for profile navigation
- Responsive design for mobile/desktop
- Loading states and error messages

### API Integration
```javascript
// Example: Search for hashtags
GET /api/hashtags/search/botdetection
→ Returns: Array of matching hashtags

// Get hashtag details with tweets
GET /api/hashtags/{id}
→ Returns: Hashtag with embedded tweets array

// Create tweet with hashtags
POST /api/tweets
Body: { author_id: 1, content: "Testing #botdetection" }
→ Backend automatically creates #botdetection hashtag
```

## Data Flow

### Tweet Creation Flow
1. User enters content: "Check out #botdetection #security"
2. Frontend sends POST /api/tweets with content
3. Backend `create_tweet()`:
   - Creates Tweet record
   - Extracts hashtags: ["botdetection", "security"]
   - For each hashtag:
     - Checks if exists (case-insensitive)
     - Creates if new
     - Associates with tweet
   - Returns Tweet with populated hashtags
4. Frontend displays tweet with linked hashtags

### Hashtag Search Flow
1. User searches "#bot"
2. Frontend calls GET /api/hashtags/search/bot
3. Backend returns matching hashtags
4. Frontend fetches each hashtag's tweets via GET /api/hashtags/{id}
5. UI displays hashtag name and all associated tweets

## Future Extension Points

### Bot Detection Integration
```python
# Example: Add analytics endpoint
@router.get("/api/analytics/bot-score/{user_id}")
def get_user_bot_score(user_id: int, db: Session = Depends(get_db)):
    """
    Returns bot detection score for a user.
    Extensible: integrate external ML model here.
    """
    user = crud.get_user(db, user_id)
    # Analyze posting patterns, hashtag usage, etc.
    # Call external bot-detection service
    return {"user_id": user_id, "bot_score": 0.85}
```

### CSV/JSON Import
```python
# Example: Add data import endpoint
@router.post("/api/import/tweets")
def import_tweets_from_json(file: UploadFile, db: Session = Depends(get_db)):
    """
    Bulk import tweets from JSON/CSV
    """
    data = json.load(file.file)
    for tweet_data in data:
        crud.create_tweet(db, TweetCreate(**tweet_data))
```

### Database Migration
The code uses SQLite by default but is easily portable to PostgreSQL:
```python
# In database.py, change:
DATABASE_URL = "postgresql://user:password@localhost/spyfind"

# Everything else remains the same (SQLAlchemy is database-agnostic)
```

## Design Principles Applied

1. **Separation of Concerns**
   - Routes handle HTTP
   - CRUD handles database operations
   - Models define data structure
   - Schemas validate data

2. **DRY (Don't Repeat Yourself)**
   - Hashtag extraction logic centralized in `extract_hashtags()`
   - CRUD operations reused across endpoints
   - Pydantic schemas for automatic validation

3. **Extensibility**
   - Modular route structure allows easy addition of new endpoints
   - CRUD functions are building blocks for complex operations
   - Database-agnostic ORM allows easy migration

4. **Clean Code**
   - Clear function naming (`create_tweet`, `extract_hashtags`)
   - Type hints throughout
   - Docstrings for public functions
   - Meaningful variable names

## Performance Considerations

### Indexes
- User.username: Unique index for login lookups
- Hashtag.name: Unique index for deduplication
- User/Tweet foreign keys: Automatic indexes from ORM

### Query Optimization
- Pagination in list endpoints (`skip`, `limit`)
- Eager loading of relationships (tweets with authors)
- Case-insensitive search using SQL functions

### Scalability Points
- Consider connection pooling for high-traffic
- Add caching for frequently searched hashtags
- Implement materialized views for analytics
- Archive old tweets to separate table

## Testing Strategy

### Unit Tests (Future)
```python
# Test hashtag extraction
assert extract_hashtags("Hello #world #spyfind") == ["world", "spyfind"]

# Test case-insensitive hashtag lookup
create_hashtag(db, "BotDetection")
assert get_hashtag_by_name(db, "botdetection") is not None
```

### Integration Tests (Future)
```python
# Test tweet creation with hashtag generation
response = client.post("/api/tweets", {
    "author_id": 1,
    "content": "New #feature"
})
assert response.status_code == 200
assert len(response.json()["hashtags"]) == 1
```

### API Tests
```bash
# Test user creation
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "display_name": "Test User"}'

# Test hashtag search
curl http://localhost:8000/api/hashtags/search/security
```

## Security Notes

### Current Implementation (Development)
- SQLite with file-based storage
- No authentication/authorization (testing tool)
- No rate limiting
- No input sanitization for XSS

### Production Considerations
- Add JWT authentication
- Implement CORS properly
- Add rate limiting (redis-based)
- Validate and sanitize all inputs
- Use environment variables for config
- Enable HTTPS
- Add input length limits
- Implement SQL injection prevention (already via SQLAlchemy ORM)

## Monitoring & Analytics (Future)

Prepare hooks for:
```python
# Log interesting events
@router.post("/api/tweets")
def create_tweet(tweet: TweetCreate, db: Session = Depends(get_db)):
    result = crud.create_tweet(db, tweet)

    # Log for analysis
    log_event({
        "event": "tweet_created",
        "user_id": tweet.author_id,
        "hashtag_count": len(result.hashtags),
        "timestamp": datetime.now()
    })

    return result
```

This enables future bot-detection analysis on:
- Tweet creation frequency
- Hashtag diversity
- User account age correlation with posting patterns
