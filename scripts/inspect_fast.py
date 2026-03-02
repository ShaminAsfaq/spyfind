import sqlite3
import os

DB_PATH = 'spyfind.db'

def inspect_fast_hashtags():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Inspecting hashtags named 'Fast' or 'FAST'...")
    cursor.execute("SELECT id, name, created_at FROM hashtags WHERE name IN ('Fast', 'FAST', 'fast')")
    hashtags = cursor.fetchall()
    
    if not hashtags:
        print("No hashtags found with those names.")
    else:
        for h in hashtags:
            h_id, name, created_at = h
            cursor.execute("SELECT COUNT(*) FROM tweet_hashtag WHERE hashtag_id = ?", (h_id,))
            count = cursor.fetchone()[0]
            print(f"ID: {h_id} | Name: {name} | CreatedAt: {created_at} | Tweet Count: {count}")
            
            # Check latest tweet for this specific hashtag
            cursor.execute("""
                SELECT t.created_at, t.content 
                FROM tweets t 
                JOIN tweet_hashtag th ON t.id = th.tweet_id 
                WHERE th.hashtag_id = ? 
                ORDER BY t.created_at DESC 
                LIMIT 1
            """, (h_id,))
            latest = cursor.fetchone()
            if latest:
                print(f"  Latest use: {latest[0]} | Content: {latest[1][:50]}...")
    
    conn.close()

if __name__ == "__main__":
    inspect_fast_hashtags()
