
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')

def fix_collation():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found!")
        return

    print("Migrating hashtags table to case-sensitive collation...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Create new table with BINARY collation
        cursor.execute("""
            CREATE TABLE hashtags_new (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                name VARCHAR NOT NULL COLLATE BINARY, 
                created_at DATETIME, 
                UNIQUE (name)
            )
        """)
        
        # 2. Copy data. 
        # If there are current duplicates that only differ by case (e.g. 'Fast' and 'FAST'),
        # they will now be allowed. If the current DB had a case-insensitive UNIQUE constraint,
        # there shouldn't even be such duplicates yet.
        cursor.execute("""
            INSERT INTO hashtags_new (id, name, created_at)
            SELECT id, name, created_at FROM hashtags
        """)
        
        # 3. Drop old table and rename new one
        # Note: We need to be careful with Foreign Keys from tweet_hashtag
        # In SQLite, we can swap them if we're careful.
        
        cursor.execute("DROP TABLE hashtags")
        cursor.execute("ALTER TABLE hashtags_new RENAME TO hashtags")
        
        # 4. Re-create index on name
        cursor.execute("CREATE INDEX ix_hashtags_name ON hashtags (name)")
        cursor.execute("CREATE INDEX ix_hashtags_id ON hashtags (id)")

        conn.commit()
        print("Successfully migrated to case-sensitive hashtags!")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_collation()
