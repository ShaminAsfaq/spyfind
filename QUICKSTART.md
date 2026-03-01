# Spyfind Quick Start Guide

## Installation (5 minutes)

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Sample Data (Optional)
```bash
python3 scripts/seed.py
```

This creates:
- 6 sample users with different profiles
- 14 sample tweets with multiple hashtags
- 14 hashtags automatically extracted

### 4. Start the Server
```bash
# Option A: Using the run script
./run.sh

# Option B: Direct uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at: **http://localhost:8000**

---

## Using Spyfind

### Frontend (http://localhost:8000)

1. **Search Hashtags**
   - Enter a hashtag name in the search bar (e.g., "botdetection")
   - Click Search or press Enter
   - View all tweets containing that hashtag

2. **Click on Usernames**
   - Click any username to see the user's profile
   - View user metadata: bio, location, followers, following
   - See all tweets from that user
   - Click "Back to Search" to return

3. **Create Tweets**
   - Click "New Tweet" button
   - Select a user from the dropdown
   - Type content with hashtags (e.g., "Testing #botdetection #testing")
   - Click Tweet
   - Hashtags are automatically created and linked!

4. **Like Tweets**
   - Click the heart icon on any tweet
   - Like count updates in real-time

### API (Programmatic Access)

#### Get All Users
```bash
curl http://localhost:8000/api/users
```

#### Get Specific User
```bash
curl http://localhost:8000/api/users/1
```

#### Search Hashtags
```bash
curl http://localhost:8000/api/hashtags/search/security
```

#### Get Hashtag with All Tweets
```bash
curl http://localhost:8000/api/hashtags/3
```

#### Create a Tweet (Auto-creates hashtags)
```bash
curl -X POST http://localhost:8000/api/tweets \
  -H "Content-Type: application/json" \
  -d '{
    "author_id": 1,
    "content": "Building #botdetection #testing systems"
  }'
```

#### Like a Tweet
```bash
curl -X POST http://localhost:8000/api/tweets/1/like
```

#### Create a User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "display_name": "New User",
    "bio": "My biography",
    "location": "City, Country",
    "followers_count": 100,
    "following_count": 50
  }'
```

---

## Sample Users (After Seeding)

| Username | Display Name | Followers | Followers | Bio |
|----------|--------------|-----------|-----------|-----|
| alice_dev | Alice Developer | 1,250 | 340 | Python enthusiast \| Bot detection researcher |
| bot_hunter | Bot Hunter | 5,840 | 120 | Detecting fake accounts since 2020 |
| security_researcher | Security Researcher | 3,200 | 450 | Cybersecurity \| Automation \| Testing |
| spam_detector | Spam Detector Bot | 8,900 | 0 | Automated spam detection system |
| test_account | Test Account | 100 | 50 | Testing purposes only |
| suspicious_user | Suspicious Activity | 15 | 5,000 | Posting frequently from multiple IPs |

---

## Key Features to Test

### 1. Hashtag Auto-Creation
Create a tweet with a brand new hashtag:
```bash
curl -X POST http://localhost:8000/api/tweets \
  -H "Content-Type: application/json" \
  -d '{"author_id": 1, "content": "Trying #brand_new_tag #another_test"}'
```

The hashtags `#brand_new_tag` and `#another_test` will be automatically created.

### 2. Many-to-Many Relationships
A single tweet can have multiple hashtags, and a hashtag can belong to multiple tweets:
```bash
# Get hashtag with all its tweets
curl http://localhost:8000/api/hashtags/3
```

### 3. Dynamic Hashtag Discovery
Search for hashtags and browse related tweets:
```bash
# Search for hashtags
curl http://localhost:8000/api/hashtags/search/test

# Get details for a specific hashtag
curl http://localhost:8000/api/hashtags/1
```

### 4. User Profiles
View detailed user information:
```bash
# Get user profile
curl http://localhost:8000/api/users/1
```

---

## Development Tips

### Run Tests
```bash
# (Test suite to be added)
# Currently: Manual testing via curl or frontend
```

### View API Documentation
FastAPI automatically generates interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database Management
```bash
# Reset database (delete spyfind.db and reseed)
rm spyfind.db
python3 scripts/seed.py
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Enable Reload Mode
The server supports auto-reload during development:
```bash
python3 -m uvicorn app.main:app --reload
```

---

## Common Operations

### Bulk Import Data (Future Feature)
You can extend the seed script to import from CSV/JSON:
```python
# In scripts/seed.py - Add function to:
# 1. Read CSV/JSON file
# 2. Parse rows
# 3. Create users and tweets
# 4. Let the system auto-create hashtags
```

### Export Tweets for Analysis
```bash
# Get all tweets as JSON
curl http://localhost:8000/api/tweets?skip=0&limit=1000 > tweets.json

# Get all users
curl http://localhost:8000/api/users?skip=0&limit=1000 > users.json

# Get all hashtags
curl http://localhost:8000/api/hashtags?skip=0&limit=1000 > hashtags.json
```

### Switch Database Backend
To use PostgreSQL instead of SQLite:

1. Update `app/database.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost/spyfind"
```

2. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

3. Run the app (SQLAlchemy handles the rest)

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or use a different port
python3 -m uvicorn app.main:app --port 8001
```

### Module Not Found Error
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Locked Error (SQLite)
```bash
# Close all connections and restart server
rm spyfind.db-journal  # If exists
# Restart the server
```

### CORS Issues
Update `app/main.py` to add CORS:
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

---

## Next Steps

1. **Explore the API**: Use http://localhost:8000/docs for interactive API testing
2. **Examine the Code**: Read `ARCHITECTURE.md` for design details
3. **Extend the System**: Add analytics endpoints, bot detection integrations, or data import
4. **Create Test Data**: Use the API to create custom users and tweets for testing
5. **Analyze Patterns**: Use the API to extract data for bot detection research

---

## API Reference Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/users | List all users |
| GET | /api/users/{id} | Get user profile |
| POST | /api/users | Create user |
| GET | /api/tweets | List all tweets |
| GET | /api/tweets/{id} | Get tweet details |
| POST | /api/tweets | Create tweet (auto-hashtags) |
| POST | /api/tweets/{id}/like | Like a tweet |
| GET | /api/hashtags | List all hashtags |
| GET | /api/hashtags/{id} | Get hashtag + tweets |
| GET | /api/hashtags/search/{query} | Search hashtags |

---

## Support

- **Documentation**: See `README.md` and `ARCHITECTURE.md`
- **Issues**: Check `/app/routes.py` for endpoint details
- **Customization**: Modify `/app/crud.py` for business logic changes

Happy testing! 🔍🤖
