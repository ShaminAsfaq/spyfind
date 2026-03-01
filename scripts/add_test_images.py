
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User

def add_test_images():
    db = SessionLocal()
    alice = db.query(User).filter(User.username == 'alice_dev').first()
    if alice:
        alice.profile_image_url = 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice'
        alice.profile_banner_url = 'https://images.unsplash.com/photo-1557683316-973673baf926'
        print("Updated alice_dev")
    
    bot = db.query(User).filter(User.username == 'bot_hunter').first()
    if bot:
        bot.profile_image_url = 'https://api.dicebear.com/7.x/bottts/svg?seed=Hunter'
        bot.profile_banner_url = 'https://images.unsplash.com/photo-1614850523296-d8c1af93d400'
        print("Updated bot_hunter")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    add_test_images()
