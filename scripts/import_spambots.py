
import sys
import os
import csv
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, BotDetection

def parse_twitter_date(date_str):
    """Parse Twitter-formatted date: 'Tue Mar 17 08:51:12 +0000 2009'"""
    if not date_str:
        return datetime.utcnow()
    try:
        # Example: 'Tue Mar 17 08:51:12 +0000 2009'
        return datetime.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y')
    except Exception:
        # Fallback to current time or maybe a dummy date
        return datetime.utcnow()

def import_spambots():
    db = SessionLocal()
    data_source_dir = os.path.join(os.getcwd(), 'data_source')
    
    # Get all subdirectories in data_source EXCEPT genuine_accounts.csv
    folders = [f for f in os.listdir(data_source_dir) 
               if os.path.isdir(os.path.join(data_source_dir, f)) 
               and f != 'genuine_accounts.csv']
    
    print(f"Found folders to process: {folders}")
    
    total_users_created = 0
    total_users_skipped = 0

    for folder in folders:
        csv_path = os.path.join(data_source_dir, folder, 'users.csv')
        if not os.path.exists(csv_path):
            print(f"⚠️  {csv_path} not found. Skipping...")
            continue
        
        print(f"Processing folder: {folder}...")
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='replace') as csvfile:
                reader = csv.DictReader(csvfile)
                
                users_created = 0
                users_skipped = 0
                
                for row in reader:
                    try:
                        user_id_str = row.get('id', '').strip()
                        if not user_id_str:
                            continue
                        user_id = int(float(user_id_str)) # Handle scientific notation if any
                        
                        # Check if user already exists
                        existing_user = db.query(User).filter(User.id == user_id).first()
                        if existing_user:
                            users_skipped += 1
                            continue
                            
                        username = row.get('screen_name', '').strip()
                        # If username is empty or extremely long/invalid, handle it
                        if not username:
                            username = f"user_{user_id}"
                            
                        # Double check if username exists (usernames must be unique in User model)
                        existing_username = db.query(User).filter(User.username == username).first()
                        if existing_username:
                            # Append user_id to username if it conflicts
                            username = f"{username}_{user_id}"

                        user = User(
                            id=user_id,
                            username=username,
                            display_name=row.get('name', '').strip() or username,
                            bio=row.get('description', '').strip() or "",
                            location=row.get('location', '').strip() or "",
                            url=row.get('url', '').strip() or "",
                            followers_count=int(row.get('followers_count', 0) or 0),
                            following_count=int(row.get('friends_count', 0) or 0),
                            posts_count=int(row.get('statuses_count', 0) or 0),
                            likes_count=int(row.get('favourites_count', 0) or 0),
                            listed_count=int(row.get('listed_count', 0) or 0),
                            profile_image_url=row.get('profile_image_url', ''),
                            profile_banner_url=row.get('profile_banner_url', ''),
                            created_at=parse_twitter_date(row.get('created_at', ''))
                        )
                        
                        bot_status = BotDetection(
                            user_id=user_id,
                            is_bot=True,
                            source=folder
                        )
                        
                        db.add(user)
                        db.add(bot_status)
                        users_created += 1
                        
                        # Periodically commit to keep memory low and database healthy
                        if users_created % 500 == 0:
                            db.commit()
                            print(f"  Processed {users_created} users in {folder}...")
                    except Exception as e:
                        print(f"  ⚠️ Skipping user row due to error: {e}")
                        continue
                
                db.commit()
                print(f"✅ Finished folder {folder}: {users_created} created, {users_skipped} skipped.")
                total_users_created += users_created
                total_users_skipped += users_skipped
                
        except Exception as e:
            print(f"❌ Error processing folder {folder}: {e}")
            db.rollback()

    print("\n" + "="*60)
    print(f"Full Bot Import completed!")
    print(f"  ✅ Total Bot Users created: {total_users_created}")
    print(f"  ⚠️  Total Users skipped: {total_users_skipped}")
    print("="*60)
    db.close()

if __name__ == "__main__":
    import_spambots()
