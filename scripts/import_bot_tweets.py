
import sys
import os
import csv
import sqlite3
import re
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection
DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')
DATA_SOURCE_DIR = os.path.join(os.getcwd(), 'data_source')

def parse_twitter_date(date_str):
    if not date_str or date_str.strip() == '':
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Format: "Wed Nov 12 20:14:48 +0000 2014"
        dt = datetime.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def safe_int(value):
    if not value or str(value).strip() == '':
        return 0
    try:
        return int(float(value))
    except:
        return 0

def extract_hashtags(content):
    if not content:
        return []
    return list(set(re.findall(r'#(\w+)', content)))

def import_bot_tweets():
    # Get all subdirectories in data_source EXCEPT genuine_accounts.csv
    folders = [f for f in os.listdir(DATA_SOURCE_DIR) 
               if os.path.isdir(os.path.join(DATA_SOURCE_DIR, f)) 
               and f != 'genuine_accounts.csv']
    
    print(f"Found folders to process for tweets: {folders}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get existing user IDs for filtering
    print("Fetching existing user IDs...")
    cursor.execute("SELECT id FROM users")
    existing_user_ids = {row[0] for row in cursor.fetchall()}
    print(f"Total existing users in DB: {len(existing_user_ids)}")
    
    total_tweets_count = 0
    batch_size = 5000
    
    start_time = time.time()
    
    # For hashtag association
    hashtag_cache = {} # name -> id
    
    for folder in folders:
        tweets_csv = os.path.join(DATA_SOURCE_DIR, folder, 'tweets.csv')
        if not os.path.exists(tweets_csv):
            print(f"⚠️  {tweets_csv} not found. Skipping...")
            continue
            
        print(f"Processing {folder}...")
        
        try:
            with open(tweets_csv, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                
                tweet_batch = []
                associations = [] # (tweet_id, hashtag_id)
                
                folder_tweets = 0
                for row in reader:
                    try:
                        tweet_id = safe_int(row.get('id'))
                        author_id = safe_int(row.get('user_id'))
                        
                        if not tweet_id or not author_id:
                            continue
                            
                        # Only import if user exists
                        if author_id not in existing_user_ids:
                            continue
                            
                        content = row.get('text', '')
                        created_at = parse_twitter_date(row.get('created_at'))
                        likes = safe_int(row.get('favorite_count'))
                        retweets = safe_int(row.get('retweet_count'))
                        comments = safe_int(row.get('reply_count'))
                        
                        tweet_batch.append((
                            tweet_id, content, author_id, created_at, likes, retweets, comments
                        ))
                        
                        # Extract hashtags
                        hashtags = extract_hashtags(content)
                        for tag_name in hashtags:
                            tag_name_lower = tag_name.lower()
                            if tag_name_lower not in hashtag_cache:
                                # Check if exists in DB
                                cursor.execute("SELECT id FROM hashtags WHERE LOWER(name) = ?", (tag_name_lower,))
                                result = cursor.fetchone()
                                if result:
                                    hashtag_cache[tag_name_lower] = result[0]
                                else:
                                    # Create new hashtag
                                    cursor.execute("INSERT INTO hashtags (name, created_at) VALUES (?, ?)", 
                                                 (tag_name, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                                    hashtag_cache[tag_name_lower] = cursor.lastrowid
                            
                            associations.append((tweet_id, hashtag_cache[tag_name_lower]))

                        if len(tweet_batch) >= batch_size:
                            # Insert tweets
                            cursor.executemany('''
                                INSERT OR REPLACE INTO tweets (
                                    id, content, author_id, created_at, likes_count, retweets_count, comments_count
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', tweet_batch)
                            
                            # Insert associations (use OR IGNORE to prevent duplicates)
                            cursor.executemany('''
                                INSERT OR IGNORE INTO tweet_hashtag (tweet_id, hashtag_id) VALUES (?, ?)
                            ''', associations)
                            
                            conn.commit()
                            total_tweets_count += len(tweet_batch)
                            folder_tweets += len(tweet_batch)
                            tweet_batch = []
                            associations = []
                            
                            elapsed = time.time() - start_time
                            print(f"  Inserted {total_tweets_count} total tweets... ({total_tweets_count/elapsed:.2f} tweets/sec)")
                            
                    except Exception as e:
                        print(f"Error processing row: {e}")
                        continue
                
                # Final batch for folder
                if tweet_batch:
                    cursor.executemany('''
                        INSERT OR REPLACE INTO tweets (
                            id, content, author_id, created_at, likes_count, retweets_count, comments_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', tweet_batch)
                    cursor.executemany('''
                        INSERT OR IGNORE INTO tweet_hashtag (tweet_id, hashtag_id) VALUES (?, ?)
                    ''', associations)
                    conn.commit()
                    total_tweets_count += len(tweet_batch)
                    folder_tweets += len(tweet_batch)
                
                print(f"✅ Finished {folder}: {folder_tweets} tweets imported.")
                
        except Exception as e:
            print(f"❌ Error processing folder {folder}: {e}")
            conn.rollback()

    conn.close()
    print("\n" + "="*60)
    print(f"Full Bot Tweet Import completed!")
    print(f"  ✅ Total Tweets created: {total_tweets_count}")
    print("="*60)

if __name__ == "__main__":
    import_bot_tweets()
