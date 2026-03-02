import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')

def revert_bot_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Reverting database changes...")
    try:
        # Create a new table with the exact original schema
        cursor.execute("""
            CREATE TABLE bot_detections_new (
                user_id INTEGER NOT NULL PRIMARY KEY, 
                is_bot BOOLEAN NOT NULL, 
                source VARCHAR, 
                created_at DATETIME, 
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Copy only the original data back
        cursor.execute("""
            INSERT INTO bot_detections_new (user_id, is_bot, source, created_at) 
            SELECT user_id, is_bot, source, created_at FROM bot_detections
        """)
        
        # Drop the modified table and rename the restored one
        cursor.execute("DROP TABLE bot_detections")
        cursor.execute("ALTER TABLE bot_detections_new RENAME TO bot_detections")
        
        conn.commit()
        print("Database perfectly restored to original state.")
    except Exception as e:
        print(f"Error restoring table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    revert_bot_table()