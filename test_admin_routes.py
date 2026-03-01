"""Test admin routes to diagnose the issue."""
import sys
from app.database import SessionLocal, init_db
from app.models import User

# Initialize database
init_db()

# Create a session
db = SessionLocal()

try:
    # Test query
    users = db.query(User).limit(5).all()
    print(f"Successfully queried {len(users)} users")
    for user in users:
        print(f"  - ID: {user.id}, Username: {user.username}, Name: {user.display_name}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
