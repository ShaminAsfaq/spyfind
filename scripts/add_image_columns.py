
import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal

def add_image_columns():
    """Add profile_image_url and profile_banner_url columns to users table."""
    db = SessionLocal()
    print("Adding image columns to users table...")

    try:
        columns = [
            "ALTER TABLE users ADD COLUMN profile_image_url TEXT",
            "ALTER TABLE users ADD COLUMN profile_banner_url TEXT"
        ]

        for column in columns:
            try:
                db.execute(text(column))
                db.commit()
                print(f"Successfully executed: {column}")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"Column already exists, skipping: {column.split('ADD COLUMN')[1].split()[0]}")
                else:
                    print(f"Error adding column: {e}")
        
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_image_columns()
