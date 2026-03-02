
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'spyfind.db')

def update_bot_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add columns if they don't exist
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(bot_detections)").fetchall()]
    
    if 'ml_prediction' not in columns:
        print("Adding ml_prediction column...")
        cursor.execute("ALTER TABLE bot_detections ADD COLUMN ml_prediction BOOLEAN")
        
    if 'ml_confidence' not in columns:
        print("Adding ml_confidence column...")
        cursor.execute("ALTER TABLE bot_detections ADD COLUMN ml_confidence INTEGER")
        
    conn.commit()
    conn.close()
    print("Table updated successfully!")

if __name__ == "__main__":
    update_bot_table()
