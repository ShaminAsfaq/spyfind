
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User

def fix_colors():
    db = SessionLocal()
    users = db.query(User).all()
    count = 0
    for u in users:
        if u.profile_color and u.profile_color.startswith('##'):
            u.profile_color = u.profile_color.replace('##', '#')
            count += 1
        if u.banner_color and u.banner_color.startswith('##'):
            u.banner_color = u.banner_color.replace('##', '#')
            count += 1
    db.commit()
    print(f"Fixed {count} color entries")
    db.close()

if __name__ == "__main__":
    fix_colors()
