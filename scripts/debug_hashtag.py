import sqlite3
import os

DB_PATH = 'spyfind.db'

def check_hashtag(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Checking hashtag: {name}")
    cursor.execute("SELECT * FROM hashtags WHERE name = ?", (name,))
    hashtag = cursor.fetchone()
    if hashtag:
        print(f"Hashtag found: ID={hashtag[0]}, Name={hashtag[1]}, CreatedAt={hashtag[2]}")
        
        # Check tweets associated with this hashtag
        cursor.execute("""
            SELECT t.id, t.content, t.created_at 
            FROM tweets t 
            JOIN tweet_hashtag th ON t.id = th.tweet_id 
            WHERE th.hashtag_id = ? 
            ORDER BY t.created_at DESC 
            LIMIT 5
        """, (hashtag[0],))
        tweets = cursor.fetchall()
        print(f"Latest tweets with this hashtag ({len(tweets)}):")
        for t in tweets:
            print(f"  ID={t[0]}, Date={t[2]}, Content={t[1]}")
    else:
        print("Hashtag NOT found in database.")
    
    conn.close()

def check_user_tweets(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\nChecking user: @{username}")
    cursor.execute("SELECT id, username, display_name FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user:
        print(f"User found: ID={user[0]}, Name={user[2]}")
        cursor.execute("SELECT id, content, created_at FROM tweets WHERE author_id = ? ORDER BY created_at DESC LIMIT 5", (user[0],))
        tweets = cursor.fetchall()
        print(f"Latest tweets from this user ({len(tweets)}):")
        for t in tweets:
            print(f"  ID={t[0]}, Date={t[2]}, Content={t[1]}")
    else:
        print("User NOT found in database.")
    conn.close()

if __name__ == "__main__":
    check_hashtag("FAST")
    check_hashtag("fast")
    check_user_tweets("youtubepixel")
