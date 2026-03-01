import csv
import sqlite3
from datetime import datetime

# Database connection
conn = sqlite3.connect(r'D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind\spyfind.db')
cursor = conn.cursor()

# CSV file path
csv_file = r'D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind\data_source\genuine_accounts.csv\users.csv'

# Function to convert Twitter date format to SQLite datetime
def parse_twitter_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
    try:
        # Format: "Tue Jun 11 11:20:35 +0000 2013"
        dt = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

# Function to convert to integer or return None
def safe_int(value):
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except:
        return None

# Function to clean string or return None
def clean_string(value):
    if not value or value.strip() == '':
        return None
    return value.strip()

# Read CSV and insert data
inserted_count = 0
skipped_count = 0

with open(csv_file, 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)

    for row in csv_reader:
        try:
            # Map CSV fields to database columns
            user_data = {
                'id': safe_int(row['id']),
                'username': clean_string(row['screen_name']),
                'display_name': clean_string(row['name']),
                'bio': clean_string(row['description']),
                'location': clean_string(row['location']),
                'url': clean_string(row['url']),
                'followers_count': safe_int(row['followers_count']),
                'following_count': safe_int(row['friends_count']),
                'posts_count': safe_int(row['statuses_count']),
                'likes_count': safe_int(row['favourites_count']),
                'listed_count': safe_int(row['listed_count']),
                'retweets_count': None,  # Not available in CSV
                'profile_color': clean_string(row['profile_link_color']),
                'banner_color': clean_string(row['profile_background_color']),
                'created_at': parse_twitter_date(row['created_at'])
            }

            # Skip if ID or username is missing
            if not user_data['id'] or not user_data['username']:
                skipped_count += 1
                continue

            # Insert into database
            cursor.execute('''
                INSERT OR REPLACE INTO users (
                    id, username, display_name, bio, location, url,
                    followers_count, following_count, posts_count, likes_count,
                    listed_count, retweets_count, profile_color, banner_color, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['id'], user_data['username'], user_data['display_name'],
                user_data['bio'], user_data['location'], user_data['url'],
                user_data['followers_count'], user_data['following_count'],
                user_data['posts_count'], user_data['likes_count'],
                user_data['listed_count'], user_data['retweets_count'],
                user_data['profile_color'], user_data['banner_color'],
                user_data['created_at']
            ))

            inserted_count += 1

        except Exception as e:
            print(f"Error processing row {row.get('id', 'unknown')}: {str(e)}")
            skipped_count += 1

# Commit changes and close connection
conn.commit()
conn.close()

print(f"\n=== Import Complete ===")
print(f"Successfully inserted: {inserted_count} users")
print(f"Skipped: {skipped_count} users")
