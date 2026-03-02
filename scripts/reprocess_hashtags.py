import sys
import os
import sqlite3
import re
from datetime import datetime
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')

def extract_hashtags(content):
    if not content:
        return []
    # Note: Using standard regex for speed
    return list(set(re.findall(r'#(\w+)', content)))

def reprocess_hashtags():
    print("🚀 Starting full hashtag reprocessing (Case-Sensitive)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_time = time.time()
    
    try:
        # 1. Clear existing associations and hashtags
        print("🧹 Clearing old hashtag data...")
        cursor.execute("DELETE FROM tweet_hashtag")
        cursor.execute("DELETE FROM hashtags")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='hashtags'")
        conn.commit()
        
        # 2. Setup processing
        print("📡 Processing tweets in batches...")
        
        # Get total for progress
        cursor.execute("SELECT COUNT(*) FROM tweets")
        total_tweets = cursor.fetchone()[0]
        print(f"Total tweets to process: {total_tweets}")

        # Fetcher
        cursor.execute("SELECT id, content, created_at FROM tweets")
        
        hashtag_cache = {} # name -> id
        associations = []
        processed_count = 0
        batch_size = 50000
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
                
            for tweet_id, content, created_at in rows:
                hashtag_names = extract_hashtags(content)
                
                for name in hashtag_names:
                    # CASE SENSITIVE CACHE
                    if name not in hashtag_cache:
                        # Insert new hashtag immediately to get ID
                        # (Doing this in a sub-cursor to not disturb the main fetch)
                        c2 = conn.cursor()
                        c2.execute("INSERT OR IGNORE INTO hashtags (name, created_at) VALUES (?, ?)", 
                                 (name, created_at))
                        if c2.rowcount > 0:
                            hashtag_id = c2.lastrowid
                        else:
                            # Already exists (edge case if re-running)
                            c2.execute("SELECT id FROM hashtags WHERE name = ?", (name,))
                            hashtag_id = c2.fetchone()[0]
                        
                        hashtag_cache[name] = hashtag_id
                    
                    associations.append((tweet_id, hashtag_cache[name]))
            
            # Commit associations in bulk
            if associations:
                c2 = conn.cursor()
                c2.executemany("INSERT OR IGNORE INTO tweet_hashtag (tweet_id, hashtag_id) VALUES (?, ?)", associations)
                associations = []
            
            processed_count += len(rows)
            conn.commit() # Periodic commit
            
            elapsed = time.time() - start_time
            percent = (processed_count / total_tweets) * 100
            print(f"  [{percent:.1f}%] Processed {processed_count}/{total_tweets} tweets... ({processed_count/elapsed:.0f} tweets/sec)")

        end_time = time.time()
        print("\n" + "="*60)
        print(f"✅ Reprocessing Complete!")
        print(f"  Total Tweets Processed: {processed_count}")
        print(f"  Distinct Hashtags Found: {len(hashtag_cache)}")
        print(f"  Total Time: {end_time - start_time:.2f} seconds")
        print("="*60)

    except Exception as e:
        print(f"❌ Error during reprocessing: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reprocess_hashtags()
