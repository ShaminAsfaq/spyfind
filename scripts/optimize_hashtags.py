
import sqlite3
import os
import time

DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')

def optimize_hashtags():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🚀 Optimizing hashtag table for performance...")
    
    try:
        # 1. Add column if it doesn't exist
        columns = [row[1] for row in cursor.execute("PRAGMA table_info(hashtags)").fetchall()]
        if 'latest_tweet_id' not in columns:
            print("Adding latest_tweet_id column...")
            cursor.execute("ALTER TABLE hashtags ADD COLUMN latest_tweet_id INTEGER REFERENCES tweets(id)")
            cursor.execute("CREATE INDEX idx_hashtags_latest_tweet ON hashtags(latest_tweet_id)")
        
        # 2. Populate the column with the latest tweet ID for every hashtag
        print("Populating latest_tweet_id (this might take a few moments for 6.4M roars)...")
        start = time.time()
        
        # This query finds the MAX tweet ID (latest) for every hashtag and updates the hashtag table
        cursor.execute("""
            UPDATE hashtags 
            SET latest_tweet_id = (
                SELECT MAX(tweet_id) 
                FROM tweet_hashtag 
                WHERE hashtag_id = hashtags.id
            )
        """)
        
        conn.commit()
        end = time.time()
        print(f"✅ Optimization complete! Took {end - start:.2f} seconds.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    optimize_hashtags()
