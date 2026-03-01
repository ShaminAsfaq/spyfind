# Spyfind Reference Card

## Quick Commands

### Setup & Running
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Seed database
python3 scripts/seed.py

# Start server
python3 -m uvicorn app.main:app --reload --port 8000

# Or use the provided script
./run.sh
```

### Access Points
| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Frontend UI |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/api/health | Health check |

## API Quick Reference

### List Resources
```bash
curl http://localhost:8000/api/users
curl http://localhost:8000/api/tweets?skip=0&limit=10
curl http://localhost:8000/api/hashtags
```

### Get Specific Item
```bash
curl http://localhost:8000/api/users/1
curl http://localhost:8000/api/tweets/1
curl http://localhost:8000/api/hashtags/3
```

### Search
```bash
curl http://localhost:8000/api/hashtags/search/botdetection
curl http://localhost:8000/api/hashtags/search/security
```

### Create Data
```bash
# Create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "display_name": "New User",
    "bio": "My bio",
    "location": "City",
    "followers_count": 100,
    "following_count": 50
  }'

# Create tweet (auto-creates hashtags)
curl -X POST http://localhost:8000/api/tweets \
  -H "Content-Type: application/json" \
  -d '{
    "author_id": 1,
    "content": "Testing #botdetection #security"
  }'
```

### Update Data
```bash
# Like a tweet
curl -X POST http://localhost:8000/api/tweets/1/like

# Like multiple times
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/tweets/1/like
done
```

## File Locations

| What | Where |
|------|-------|
| Backend code | `app/` |
| API routes | `app/routes.py` |
| Database models | `app/models.py` |
| CRUD operations | `app/crud.py` |
| Frontend | `static/index.html` |
| Database | `spyfind.db` |
| Config | `requirements.txt` |
| Data seed | `scripts/seed.py` |

## Key Concepts

### Hashtag Extraction
When a tweet is created with `"Hello #world #test"`:
1. System extracts: `["world", "test"]`
2. Creates hashtags if new
3. Associates with tweet
4. No manual management needed

### Many-to-Many
One tweet can have multiple hashtags:
```
Tweet #1: "#security #testing #botdetection"
         ↓ ↓ ↓
Hashtag: security (also in tweets #2, #5)
Hashtag: testing (also in tweets #3, #4)
Hashtag: botdetection (also in tweets #7, #8)
```

### User Profiles
Each user has:
- Basic info (username, display_name, bio, location)
- Stats (followers_count, following_count)
- Timestamps (created_at)
- Tweets (1:N relationship)

## Database Reset

```bash
# Delete old database
rm spyfind.db

# Reseed with fresh data
python3 scripts/seed.py

# Restart server
python3 -m uvicorn app.main:app
```

## Debugging

### Check Server Status
```bash
curl http://localhost:8000/health
```

### View Server Logs
```bash
# Check if server is running
ps aux | grep uvicorn

# Kill server if needed
kill -9 <PID>
```

### Inspect Database
```bash
# Query with sqlite3
sqlite3 spyfind.db

# In sqlite3 shell:
.tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM tweets;
SELECT * FROM hashtags LIMIT 5;
```

### Test API with Python
```python
import requests

# Get all users
response = requests.get('http://localhost:8000/api/users')
users = response.json()
print(f"Found {len(users)} users")

# Create tweet
tweet = {
    "author_id": 1,
    "content": "Testing #api #python"
}
response = requests.post('http://localhost:8000/api/tweets', json=tweet)
new_tweet = response.json()
print(f"Created tweet {new_tweet['id']}")

# Search hashtags
response = requests.get('http://localhost:8000/api/hashtags/search/api')
hashtags = response.json()
print(f"Found {len(hashtags)} hashtags")
```

## Common Issues & Fixes

### Port Already in Use
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python3 -m uvicorn app.main:app --port 8001
```

### Module Not Found
```bash
# Activate venv
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Database Locked
```bash
# Remove lock file
rm spyfind.db-journal

# Restart server
```

### CORS Issues (When Integrating)
Add to `app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Tips

### Pagination
```bash
# Get 20 tweets, skip first 10
curl "http://localhost:8000/api/tweets?skip=10&limit=20"

# Use with large datasets
curl "http://localhost:8000/api/users?skip=0&limit=100"
```

### Batch Operations
```bash
# Get all data at once
curl "http://localhost:8000/api/tweets?skip=0&limit=10000" > tweets.json
curl "http://localhost:8000/api/users?skip=0&limit=10000" > users.json
```

## Extension Points

### Add New Endpoint
1. Add route in `app/routes.py`
2. Add CRUD function in `app/crud.py`
3. Add schema in `app/schemas.py`
4. Test with curl or Swagger UI

### Add New Model
1. Define in `app/models.py`
2. Run database migration
3. Add schemas in `app/schemas.py`
4. Add routes in `app/routes.py`

### Switch Database
Change `DATABASE_URL` in `app/database.py`:
```python
# SQLite (default)
DATABASE_URL = "sqlite:///./spyfind.db"

# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/spyfind"
```

## Sample Data

### Users (Auto-created by seed)
1. alice_dev - Developer (1,250 followers)
2. bot_hunter - Researcher (5,840 followers)
3. security_researcher - Analyst (3,200 followers)
4. spam_detector - Bot (8,900 followers)
5. test_account - Generic (100 followers)
6. suspicious_user - Bot-like (15 followers)

### Popular Hashtags
- #botdetection (14 tweets)
- #security (5 tweets)
- #testing (6 tweets)
- #python (2 tweets)
- #ml (2 tweets)

## Frontend Features

### Search
- Type hashtag name
- Press Enter or click Search
- Results show all tweets with that hashtag

### Profiles
- Click username to view profile
- See bio, location, followers
- View all user's tweets

### Create Tweet
- Click "New Tweet"
- Select user from dropdown
- Type content (include #hashtags)
- Click Tweet
- Hashtags auto-created!

### Like
- Click heart on any tweet
- Counter increments
- Persists in database

## Documentation Files

| File | Contains |
|------|----------|
| README.md | Feature overview & setup |
| QUICKSTART.md | 5-minute getting started |
| ARCHITECTURE.md | Design & implementation |
| BOT_DETECTION_INTEGRATION.md | Integration patterns |
| PROJECT_SUMMARY.md | Complete overview |
| REFERENCE_CARD.md | This file |

## Example Workflows

### Create Test Dataset
```bash
# Seed initial data
python3 scripts/seed.py

# Create additional user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testbot", "display_name": "Test Bot"}'

# Create tweets from new user
curl -X POST http://localhost:8000/api/tweets \
  -H "Content-Type: application/json" \
  -d '{"author_id": 7, "content": "#test #automation"}'

# Verify
curl http://localhost:8000/api/hashtags/search/automation
```

### Analyze User Activity
```bash
# Get user profile
curl http://localhost:8000/api/users/1 | jq '.followers_count'

# Count user's tweets
curl http://localhost:8000/api/tweets | jq '[.[] | select(.author_id == 1)] | length'

# Find all hashtags by user
curl http://localhost:8000/api/tweets | \
  jq '[.[] | select(.author_id == 1) | .hashtags[].name] | unique'
```

## Version Info
- Spyfind: 1.0.0
- FastAPI: 0.115.0
- SQLAlchemy: 2.0.35
- Python: 3.10+
- Status: Production Ready ✓

---

For more help, see the full documentation files included in the project.
