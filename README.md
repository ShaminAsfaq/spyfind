# Spyfind - Complete Beginner's Guide

## 👋 What is Spyfind?

**Spyfind** is a fake Twitter/X-like website that you can run on your computer. It lets you:
- Create fake users
- Post fake tweets with hashtags (#)
- Search for tweets by hashtag
- View user profiles
- Test bot-detection code

Think of it as a **sandbox Twitter** - a safe testing environment where you can experiment.

---

## 🚀 Getting Started (Step by Step)

### Step 1: Install Python Dependencies

Dependencies are just extra tools Python needs. We list them in `requirements.txt`.

First, open your terminal/command prompt and go to the `spyfind` folder:

```bash
cd /Users/islamkastero/spyfind
```

**Create a virtual environment** (think of it as a separate Python workspace):

```bash
python3 -m venv venv
```

**Activate it** (turn it on):

- **On Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```

You should see `(venv)` at the start of your terminal now.

**Install the required tools:**

```bash
pip install -r requirements.txt
```

This downloads and installs:
- **FastAPI** - Makes the server work
- **Uvicorn** - Runs the server
- **SQLAlchemy** - Talks to the database
- **Pydantic** - Validates data
- **python-dateutil** - Handles dates

### Step 2: Populate the Database with Sample Data

The database needs some fake users and tweets to start with:

```bash
python3 scripts/seed.py
```

This creates:
- **6 fake users** (alice_dev, bot_hunter, etc.)
- **14 fake tweets** with hashtags
- **14 hashtags** automatically created

You should see something like:
```
🌱 Seeding database with sample data...
✓ Created user: @alice_dev
✓ Created user: @bot_hunter
...
✅ Database seeding complete!
```

### Step 3: Start the Servers

Spyfind now runs on a **dual-server architecture** (separated Frontend and Backend):

- **Backend (API):** Handles the database, ML model, and data logic. Runs on port **8000**.
- **Frontend (UI):** Handles the website interface. Runs on port **3000**.

#### Automatic Startup (Recommended)
Use the provided script to start both servers at once:

- **On Windows:**
  ```bash
  run_servers.bat
  ```
- **On Mac/Linux:**
  ```bash
  chmod +x run_servers.sh
  ./run_servers.sh
  ```

#### Manual Startup
If you want to run them in separate terminal windows:

**Terminal 1 (Backend):**
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn frontend.main:app --host 0.0.0.0 --port 3000 --reload
```

**Visit the website:** `http://localhost:3000`
**View the API documentation:** `http://localhost:8000/docs`

### Step 4: Stop the Servers

Press **Ctrl + C** in each terminal window to stop the servers.

---

## 🎨 Using the Website

### Search for Hashtags

1. Type a hashtag name in the search bar (e.g., `botdetection`)
2. Click **Search** or press Enter
3. You'll see all tweets with that hashtag

### View a User's Profile

1. Click on any **username** (like `@alice_dev`)
2. You'll see:
   - User's bio
   - Location
   - Followers/Following counts
   - All their tweets

3. Click **"← Back to Search"** to go back

### Create a Tweet

1. Click the **"New Tweet"** button
2. Select a user from the dropdown
3. Type your tweet and include **#hashtags** (e.g., `Testing #botdetection`)
4. Click **Tweet**
5. The hashtags are automatically created! 🎯

### Like a Tweet

1. Click the ❤ heart icon on any tweet
2. The number goes up
3. It's saved in the database

---

## 📱 Using the API (For Programmers)

The API lets you interact with Spyfind using **code** instead of clicking buttons.

### What's an API?

An API is like a menu at a restaurant:
- You make a "request" (order)
- You get a "response" (food arrives)

### API Basics

**All API endpoints start with:** `http://localhost:8000/api`

They return data as **JSON** (structured text).

### Users API

#### Get all users
```bash
curl http://localhost:8000/api/users
```

**Response example:**
```json
[
  {
    "id": 1,
    "username": "alice_dev",
    "display_name": "Alice Developer",
    "bio": "Python enthusiast",
    "location": "San Francisco, CA",
    "followers_count": 1250,
    "following_count": 340,
    "created_at": "2025-10-28T01:11:35.306787"
  }
]
```

#### Get a specific user
```bash
curl http://localhost:8000/api/users/1
```

#### Create a new user
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "display_name": "New User",
    "bio": "My biography",
    "location": "New York",
    "followers_count": 100,
    "following_count": 50
  }'
```

**What each field means:**
- `username` - Like @twitter_handle (must be unique, no spaces)
- `display_name` - The fancy name shown
- `bio` - Their description
- `location` - Where they say they're from
- `followers_count` - How many people follow them
- `following_count` - How many people they follow

### Tweets API

#### Get all tweets
```bash
curl http://localhost:8000/api/tweets
```

#### Get a specific tweet
```bash
curl http://localhost:8000/api/tweets/1
```

#### Create a tweet
```bash
curl -X POST http://localhost:8000/api/tweets \
  -H "Content-Type: application/json" \
  -d '{
    "author_id": 1,
    "content": "Hello world! #botdetection #testing"
  }'
```

**What happens:**
1. The tweet is saved with the content
2. Spyfind finds all #hashtags in the content
3. It creates new hashtags if they don't exist
4. It links the tweet to those hashtags
5. **All automatic!** 🤖

#### Like a tweet
```bash
curl -X POST http://localhost:8000/api/tweets/1/like
```

This adds 1 to the like count.

### Hashtags API

#### Get all hashtags
```bash
curl http://localhost:8000/api/hashtags
```

#### Search for hashtags
```bash
curl http://localhost:8000/api/hashtags/search/security
```

This finds hashtags that contain "security" (like `#security`, `#security-check`, etc.)

#### Get a hashtag with all its tweets
```bash
curl http://localhost:8000/api/hashtags/3
```

**Response includes:**
- The hashtag name
- All tweets that use this hashtag
- Information about each tweet and its author

---

## 🗂️ Understanding the Code Structure

### What are the main files?

```
spyfind/
│
├── app/                    # The "brain" of the application
│   ├── main.py            # Starts the server (entry point)
│   ├── database.py        # Talks to SQLite database
│   ├── models.py          # Defines data structure
│   ├── schemas.py         # Validates input data
│   ├── crud.py            # Functions to work with data
│   └── routes.py          # API endpoints
│
├── static/
│   └── index.html         # The website you see
│
├── scripts/
│   └── seed.py            # Creates sample data
│
├── spyfind.db             # The database (all saved data)
├── requirements.txt       # List of Python tools needed
└── README.md             # This file!
```

### The Main Classes (What do they do?)

#### 1. **User** (in `app/models.py`)

A User represents a person on the fake Twitter.

```python
class User:
    id              # Unique number (1, 2, 3...)
    username        # Like @alice_dev (must be unique)
    display_name    # Like "Alice Developer"
    bio            # Description about them
    location       # Where they're from
    followers_count # How many people follow them
    following_count # How many people they follow
    created_at     # When account was created
```

**What it can do:**
- Store user information
- Link to tweets (one user can have many tweets)

#### 2. **Tweet** (in `app/models.py`)

A Tweet represents one post.

```python
class Tweet:
    id           # Unique number
    content      # The text they wrote
    author_id    # Who wrote it (links to User)
    created_at   # When it was posted
    likes_count  # How many likes it has
```

**What it can do:**
- Store tweet text
- Link to the user who wrote it
- Link to multiple hashtags

#### 3. **Hashtag** (in `app/models.py`)

A Hashtag is a topic like `#botdetection`.

```python
class Hashtag:
    id         # Unique number
    name       # Like "botdetection" (just the word, not the #)
    created_at # When hashtag was first created
```

**What it can do:**
- Store hashtag names
- Link to many tweets that use it

---

## 🔧 Main Functions (How to use them)

All these are in `app/crud.py` and can be used in your code:

### User Functions

#### `create_user()`
**What it does:** Creates a new user

**How to use:**
```python
from app.crud import create_user
from app.schemas import UserCreate
from app.database import SessionLocal

db = SessionLocal()
new_user = UserCreate(
    username="john_doe",
    display_name="John Doe",
    bio="I like Python",
    location="Boston",
    followers_count=500,
    following_count=200
)
user = create_user(db, new_user)
db.close()
```

#### `get_user()`
**What it does:** Gets one user by ID

**How to use:**
```python
from app.crud import get_user
from app.database import SessionLocal

db = SessionLocal()
user = get_user(db, user_id=1)
print(user.username)  # Outputs: "alice_dev"
db.close()
```

#### `get_users()`
**What it does:** Gets all users (with optional pagination)

**How to use:**
```python
from app.crud import get_users
from app.database import SessionLocal

db = SessionLocal()
users = get_users(db, skip=0, limit=10)  # Get first 10 users
print(len(users))  # Outputs: number of users
db.close()
```

### Tweet Functions

#### `create_tweet()`
**What it does:** Creates a new tweet AND automatically creates hashtags

**How to use:**
```python
from app.crud import create_tweet
from app.schemas import TweetCreate
from app.database import SessionLocal

db = SessionLocal()
new_tweet = TweetCreate(
    author_id=1,
    content="I love #python and #botdetection!"
)
tweet = create_tweet(db, new_tweet)
# Hashtags "#python" and "#botdetection" are automatically created!
db.close()
```

**Important:** This function:
1. Saves the tweet
2. Finds all #words (hashtags)
3. Creates new hashtags if they don't exist
4. Links everything together

#### `extract_hashtags()`
**What it does:** Finds all #hashtags in text

**How to use:**
```python
from app.crud import extract_hashtags

text = "I love #python and #botdetection and #testing!"
hashtags = extract_hashtags(text)
print(hashtags)  # Outputs: ['python', 'botdetection', 'testing']
```

#### `get_tweet()`
**What it does:** Gets one tweet by ID

**How to use:**
```python
from app.crud import get_tweet
from app.database import SessionLocal

db = SessionLocal()
tweet = get_tweet(db, tweet_id=5)
print(tweet.content)
db.close()
```

#### `get_tweets()`
**What it does:** Gets all tweets

**How to use:**
```python
from app.crud import get_tweets
from app.database import SessionLocal

db = SessionLocal()
tweets = get_tweets(db, skip=0, limit=20)  # Get first 20
db.close()
```

#### `like_tweet()`
**What it does:** Adds 1 to a tweet's like count

**How to use:**
```python
from app.crud import like_tweet
from app.database import SessionLocal

db = SessionLocal()
tweet = like_tweet(db, tweet_id=1)
print(tweet.likes_count)  # Now increased by 1
db.close()
```

### Hashtag Functions

#### `create_hashtag()`
**What it does:** Creates a new hashtag (or returns existing one)

**How to use:**
```python
from app.crud import create_hashtag
from app.database import SessionLocal

db = SessionLocal()
hashtag = create_hashtag(db, name="botdetection")
# If #botdetection already exists, it returns that instead
db.close()
```

#### `get_hashtag()`
**What it does:** Gets one hashtag by ID

**How to use:**
```python
from app.crud import get_hashtag
from app.database import SessionLocal

db = SessionLocal()
hashtag = get_hashtag(db, hashtag_id=3)
print(hashtag.name)  # Outputs: "botdetection"
db.close()
```

#### `search_hashtags()`
**What it does:** Finds hashtags that match a search term

**How to use:**
```python
from app.crud import search_hashtags
from app.database import SessionLocal

db = SessionLocal()
results = search_hashtags(db, query="sec")
# Finds hashtags like: security, secret, etc.
for hashtag in results:
    print(hashtag.name)
db.close()
```

#### `get_tweets_by_hashtag()`
**What it does:** Gets all tweets that use a specific hashtag

**How to use:**
```python
from app.crud import get_tweets_by_hashtag
from app.database import SessionLocal

db = SessionLocal()
tweets = get_tweets_by_hashtag(db, hashtag_id=3)
for tweet in tweets:
    print(tweet.content)
db.close()
```

---

## 📊 Understanding the Database

### What's a Database?

A database is like a filing cabinet - it stores all your data permanently on disk.

Spyfind uses **SQLite**, which stores everything in one file: `spyfind.db`

### The Three Tables

#### Users Table
Stores information about people:

| id | username | display_name | bio | location | followers_count | following_count | created_at |
|---|---|---|---|---|---|---|---|
| 1 | alice_dev | Alice Developer | Python enthusiast | San Francisco | 1250 | 340 | 2025-10-28T... |
| 2 | bot_hunter | Bot Hunter | Researcher | New York | 5840 | 120 | 2025-10-28T... |

#### Tweets Table
Stores posts:

| id | content | author_id | created_at | likes_count |
|---|---|---|---|---|
| 1 | Hello world #test | 1 | 2025-10-28T... | 5 |
| 2 | Another post #security | 2 | 2025-10-28T... | 12 |

#### Hashtags Table
Stores hashtag names:

| id | name | created_at |
|---|---|---|
| 1 | security | 2025-10-28T... |
| 2 | test | 2025-10-28T... |

#### Tweet_Hashtag Table (Connector)
Links tweets to hashtags:

| tweet_id | hashtag_id |
|---|---|
| 1 | 2 |
| 2 | 1 |

This says: "Tweet #1 uses hashtag #2 (test), and Tweet #2 uses hashtag #1 (security)"

---

## ➕ How to Add Users (Step by Step)

### Method 1: Using the Website UI

1. Click **"New Tweet"** button
2. The dropdown shows all users
3. To add a new user, use **Method 2** or **Method 3** below first

### Method 2: Using the Command Line (curl)

Open a terminal (with the server running in another terminal):

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mynewtester",
    "display_name": "My New Tester",
    "bio": "Testing bot detection",
    "location": "Boston, MA",
    "followers_count": 50,
    "following_count": 100
  }'
```

**Explanation:**
- `-X POST` = We're creating something new
- `http://localhost:8000/api/users` = Where to send it
- `-H "Content-Type: application/json"` = The data is JSON format
- `-d '{...}'` = The data itself

### Method 3: Using Python Code

Create a file called `add_user.py`:

```python
import requests

# Tell the API where to find Spyfind
API_URL = "http://localhost:8000"

# The new user data
new_user = {
    "username": "spybot",
    "display_name": "Spy Bot",
    "bio": "I'm a test bot",
    "location": "Cyberspace",
    "followers_count": 10,
    "following_count": 5000
}

# Send the request
response = requests.post(f"{API_URL}/api/users", json=new_user)

# Check if it worked
if response.status_code == 200:
    user = response.json()
    print(f"✅ Created user: {user['username']}")
    print(f"   ID: {user['id']}")
else:
    print(f"❌ Error: {response.text}")
```

**Run it:**
```bash
python3 add_user.py
```

### Method 4: Using Python Directly in Code

```python
from app.database import SessionLocal
from app.crud import create_user
from app.schemas import UserCreate

# Open database connection
db = SessionLocal()

# Create the user data
user_data = UserCreate(
    username="testuser123",
    display_name="Test User 123",
    bio="Learning Spyfind",
    location="London",
    followers_count=0,
    following_count=0
)

# Create the user
new_user = create_user(db, user_data)

# Done!
print(f"Created user: {new_user.username}")

# Close the database
db.close()
```

---

## 🐛 Troubleshooting

### Problem: "Port 8000 is already in use"

**Cause:** Another program is using that port

**Solution:**
```bash
# Use a different port
python3 -m uvicorn app.main:app --port 8001
```

Then visit: `http://localhost:8001`

### Problem: "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** You haven't installed dependencies

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: "Database is locked"

**Cause:** The database file is in use

**Solution:**
```bash
# Stop the server (Ctrl+C)
# Remove the lock file
rm spyfind.db-journal
# Start the server again
```

### Problem: "No such table: users"

**Cause:** Database needs to be initialized

**Solution:**
```bash
# The database is created automatically when the server starts
# But you can manually seed data:
python3 scripts/seed.py
```

---

## 📚 Learning Resources

### To understand more:

1. **ARCHITECTURE.md** - How the code is organized
2. **QUICKSTART.md** - Another quick guide
3. **REFERENCE_CARD.md** - Commands cheat sheet
4. **BOT_DETECTION_INTEGRATION.md** - How to add bot detection

### Helpful links:

- **FastAPI docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy docs:** https://docs.sqlalchemy.org/
- **curl tutorial:** https://curl.se/docs/manual.html

---

## 🎯 Quick Summary

**Spyfind is:**
- A fake Twitter to test with
- Has Users, Tweets, and Hashtags
- Hashtags are auto-created from tweets
- Everything is connected in the database
- Can be used through a website or API

**To use it:**
1. Install dependencies: `pip install -r requirements.txt`
2. Seed data: `python3 scripts/seed.py`
3. Start server: `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Visit: `http://localhost:8000`

**Main things you can do:**
- Create users (via API or code)
- Post tweets with #hashtags
- Search for #hashtags
- Like tweets
- View profiles

---

## ✨ That's It!

You now know everything you need to use and understand Spyfind. Happy testing! 🚀

Feel free to explore the code, modify it, and make it your own!
