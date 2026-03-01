# Spyfind Data Management Guide
## For Your FYP Bot Detector Integration

## 📊 Database Structure

### Location
```
/Users/islamkastero/spyfind/spyfind.db
```

This is a **SQLite database** containing all user and post data.

### Tables Available
1. **users** - User profiles with bot detection features
2. **tweets** - Posts/roars
3. **hashtags** - Hashtag data
4. **reposts** - Repost relationships
5. **comments** - Comments on posts

## 🔧 Adding New User Data

### Method 1: CSV Import (Recommended for Bulk Data)

#### Step 1: Create Your CSV File
Format: `username,display_name,bio,location,url,followers_count,following_count,posts_count,likes_count,listed_count,profile_color,banner_color`

Example CSV (`my_users.csv`):
```csv
username,display_name,bio,location,url,followers_count,following_count,posts_count,likes_count,listed_count,profile_color,banner_color
bot_account1,Bot Account,Suspicious bot,Unknown,,100,5000,10,2,0,#1da1f2,#ffffff
real_user1,John Doe,Real person here,NYC,https://john.com,1500,800,250,5000,50,#e74c3c,#f3e5f5
```

#### Step 2: Import the CSV
```bash
cd /Users/islamkastero/spyfind
python scripts/import_users_from_csv.py import my_users.csv
```

#### Step 3: Verify Import
Check the website at http://localhost:8000 or use the API:
```bash
curl http://localhost:8000/api/users
```

### Method 2: Export Current Data
Export existing users to analyze/modify:
```bash
python scripts/import_users_from_csv.py export current_users.csv
```

### Method 3: API Endpoint (Programmatic)
Use this for your bot detector to add accounts it discovers:

```python
import requests

new_user = {
    "username": "suspect_bot",
    "display_name": "Suspect Bot",
    "bio": "Automated account",
    "location": "",
    "url": "",
    "followers_count": 10000,
    "following_count": 50,
    "posts_count": 5000,
    "likes_count": 100,
    "listed_count": 1,
    "retweets_count": 0,
    "profile_color": "#1da1f2",
    "banner_color": "#ffffff"
}

response = requests.post("http://localhost:8000/api/users", json=new_user)
print(response.json())
```

## 🤖 For Your FYP Bot Detector

### Available API Endpoints for ML Analysis

#### Get All Users
```bash
GET http://localhost:8000/api/users
```

#### Get Specific User
```bash
GET http://localhost:8000/api/users/{user_id}
```

#### Search Users
```bash
GET http://localhost:8000/api/users
# Then filter in your code by username/display_name
```

#### Get Hashtag Information
```bash
GET http://localhost:8000/api/hashtags/{hashtag_id}
GET http://localhost:8000/api/hashtags/search/{query}
```

### Key Features for Bot Detection

Each user object contains these ML-ready features:

```json
{
  "id": 1,
  "username": "bot_hunter_99",
  "display_name": "Bot Hunter",
  "bio": "Detecting fake accounts since 2020",
  "location": "New York",
  "url": "https://bothunter.com",
  "followers_count": 5000,
  "following_count": 1200,
  "posts_count": 850,
  "likes_count": 25000,
  "listed_count": 150,
  "retweets_count": 0,
  "profile_color": "#e74c3c",
  "banner_color": "#fff3e0",
  "created_at": "2023-05-15T10:30:00"
}
```

### Calculated Ratios for ML (Examples)

Your bot detector can calculate:

1. **Followers/Following Ratio**
   ```python
   ratio = followers_count / max(following_count, 1)
   # Bots often have low followers, high following
   ```

2. **Engagement Rate**
   ```python
   engagement = likes_count / max(posts_count, 1)
   # Bots typically have low engagement
   ```

3. **Listed Ratio**
   ```python
   listed_ratio = listed_count / max(followers_count, 1)
   # Real accounts get listed more frequently
   ```

4. **Account Activity**
   ```python
   posts_per_day = posts_count / account_age_days
   # Bots often post excessively
   ```

5. **Profile Completeness**
   ```python
   completeness = sum([
       bool(bio),
       bool(location),
       bool(url),
       profile_color != "#1da1f2"  # Custom color
   ]) / 4
   ```

## 📈 Example Bot Detection Workflow

```python
import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. Fetch all users from Spyfind
response = requests.get("http://localhost:8000/api/users")
users = response.json()

# 2. Convert to DataFrame
df = pd.DataFrame(users)

# 3. Calculate features
df['followers_following_ratio'] = df['followers_count'] / df['following_count'].replace(0, 1)
df['engagement_rate'] = df['likes_count'] / df['posts_count'].replace(0, 1)
df['listed_ratio'] = df['listed_count'] / df['followers_count'].replace(0, 1)
df['has_url'] = df['url'].notna().astype(int)
df['has_bio'] = (df['bio'] != '').astype(int)

# 4. Your ML model
features = ['followers_count', 'following_count', 'posts_count',
            'followers_following_ratio', 'engagement_rate', 'listed_ratio',
            'has_url', 'has_bio']

# Train/predict bot scores
# model.predict(df[features])

# 5. Calculate hashtag trust score
hashtag_response = requests.get("http://localhost:8000/api/hashtags/search/security")
hashtag = hashtag_response.json()[0]
hashtag_tweets = requests.get(f"http://localhost:8000/api/hashtags/{hashtag['id']}").json()

# Analyze users who posted this hashtag
user_ids = [tweet['author']['id'] for tweet in hashtag_tweets['tweets']]
hashtag_users = df[df['id'].isin(user_ids)]

# Calculate trust score
trust_score = hashtag_users['bot_probability'].mean()  # Your ML output
print(f"Hashtag #{hashtag['name']} trust score: {trust_score:.2%}")
```

## 🗄️ Direct Database Access (Advanced)

If you need direct database access:

```python
import sqlite3

conn = sqlite3.connect('/Users/islamkastero/spyfind/spyfind.db')
cursor = conn.cursor()

# Query all users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Get column names
column_names = [description[0] for description in cursor.description]

conn.close()
```

## 📝 CSV Template for Your Bot Dataset

Create `bot_dataset.csv` with this structure:

```csv
username,display_name,bio,location,url,followers_count,following_count,posts_count,likes_count,listed_count,is_bot
bot_account1,Bot1,spam,,,50000,10,10000,50,0,1
real_user1,Real User,human,NYC,https://real.com,1000,800,200,3000,25,0
```

Then import and use for training:
```bash
python scripts/import_users_from_csv.py import bot_dataset.csv
```

## 🔄 Workflow Summary

1. **Collect Data** → Add users via CSV or API
2. **Access Data** → Use GET /api/users endpoint
3. **Extract Features** → Calculate ratios and metrics
4. **Train ML Model** → Use sklearn/tensorflow/pytorch
5. **Analyze Hashtags** → Get hashtag users and score them
6. **Return Trust Score** → Based on bot probability

## 📚 Example Files Included

- `/Users/islamkastero/spyfind/example_users.csv` - Sample CSV template
- `/Users/islamkastero/spyfind/scripts/import_users_from_csv.py` - Import/export script

## 🚀 Quick Start

```bash
# 1. Export current users
cd /Users/islamkastero/spyfind
python scripts/import_users_from_csv.py export my_current_users.csv

# 2. Edit CSV or create new dataset

# 3. Import new users
python scripts/import_users_from_csv.py import new_bot_dataset.csv

# 4. Access via API for your ML model
curl http://localhost:8000/api/users
```

## 💡 Tips for Your FYP

1. **Feature Engineering**: The current fields give you a solid baseline for bot detection
2. **Real-time Integration**: Use the API endpoints to fetch data as needed
3. **Bulk Operations**: Use CSV for initial dataset, API for live detection
4. **Database Backup**: Run export regularly to backup your dataset
5. **Hashtag Analysis**: Combine user features with hashtag posting patterns

Good luck with your FYP! 🎓
