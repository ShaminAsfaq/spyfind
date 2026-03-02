
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models import User, BotDetection

def init_bot_table():
    print("Creating bot_detections table...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have entries in bot_detections
        count = db.query(BotDetection).count()
        if count > 0:
            print(f"BotDetection table already has {count} entries.")
            return

        print("Marking existing users as humans...")
        users = db.query(User).all()
        bot_detections = []
        for user in users:
            bot_detections.append(BotDetection(
                user_id=user.id,
                is_bot=False,
                source="initial_import",
                created_at=datetime.utcnow()
            ))
        
        # Bulk insert
        db.bulk_save_objects(bot_detections)
        db.commit()
        print(f"Successfully marked {len(users)} users as humans.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_bot_table()
