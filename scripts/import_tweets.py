
import sys
import os
import csv
import sqlite3
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'spyfind.db')
TWEETS_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_source', 'genuine_accounts.csv', 'tweets.csv')

def parse_twitter_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
    try:
        # Format: "Fri May 01 00:18:11 +0000 2015"
        dt = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return None

def safe_int(value):
    if not value or value.strip() == '':
        return 0
    try:
        return int(float(value)) # Handle potential float strings
    except:
        return 0

def import_tweets():
    if not os.path.exists(TWEETS_CSV):
        print(f"Error: {TWEETS_CSV} not found!")
        return

    print(f"Starting import from {TWEETS_CSV}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Disable foreign keys temporarily for performance and to avoid issues with missing users
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Get set of existing user IDs to skip tweets from non-existent users if we want
    # For now, we'll try to insert all and see what happens.
    
    start_time = time.time()
    count = 0
    batch_size = 10000
    batch = []
    
    try:
        with open(TWEETS_CSV, 'r', encoding='utf-8', errors='replace') as f:
            # We use a custom reader because some rows might have issues
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    tweet_id = safe_int(row.get('id'))
                    author_id = safe_int(row.get('user_id'))
                    content = row.get('text', '')
                    created_at = parse_twitter_date(row.get('created_at'))
                    likes = safe_int(row.get('favorite_count'))
                    retweets = safe_int(row.get('retweet_count'))
                    comments = safe_int(row.get('reply_count'))
                    
                    if not tweet_id or not author_id:
                        continue
                        
                    batch.append((
                        tweet_id, content, author_id, created_at, likes, retweets, comments
                    ))
                    
                    if len(batch) >= batch_size:
                        cursor.executemany('''
                            INSERT OR REPLACE INTO tweets (
                                id, content, author_id, created_at, likes_count, retweets_count, comments_count
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', batch)
                        conn.commit()
                        count += len(batch)
                        batch = []
                        elapsed = time.time() - start_time
                        print(f"Inserted {count} tweets... ({count/elapsed:.2f} tweets/sec)")
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
            
            # Insert remaining
            if batch:
                cursor.executemany('''
                    INSERT OR REPLACE INTO tweets (
                        id, content, author_id, created_at, likes_count, retweets_count, comments_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                conn.commit()
                count += len(batch)
                
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        conn.close()
        
    end_time = time.time()
    print(f"\nImport complete!")
    print(f"Total tweets: {count}")
    print(f"Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    import_tweets()
