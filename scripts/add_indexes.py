
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')

def add_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found!")
        return

    print("Adding indexes to tweet_hashtag table...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if indexes already exist
        cursor.execute("PRAGMA index_list(tweet_hashtag)")
        indexes = cursor.fetchall()
        
        index_names = [idx[1] for idx in indexes]
        
        if 'idx_tweet_hashtag_tweet_id' not in index_names:
            print("Creating index on tweet_id...")
            cursor.execute("CREATE INDEX idx_tweet_hashtag_tweet_id ON tweet_hashtag(tweet_id)")
            
        if 'idx_tweet_hashtag_hashtag_id' not in index_names:
            print("Creating index on hashtag_id...")
            cursor.execute("CREATE INDEX idx_tweet_hashtag_hashtag_id ON tweet_hashtag(hashtag_id)")
        
        # Also let's check tweets table (author_id)
        cursor.execute("PRAGMA index_list(tweets)")
        tweet_indexes = cursor.fetchall()
        tweet_index_names = [idx[1] for idx in tweet_indexes]
        
        if 'idx_tweets_author_id' not in tweet_index_names:
             print("Creating index on tweets.author_id...")
             cursor.execute("CREATE INDEX idx_tweets_author_id ON tweets(author_id)")

        conn.commit()
        print("Indexes added successfully!")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_indexes()
