import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.crud import get_top_hashtags_by_date
import time

def test_latest_hashtags():
    db = SessionLocal()
    print("Fetching latest hashtags (by latest tweet use)...")
    start = time.time()
    results = get_top_hashtags_by_date(db, limit=10)
    end = time.time()
    
    print(f"Time taken: {end - start:.4f} seconds")
    print("Results:")
    for r in results:
        print(f"  #{r['name']} (ID={r['id']}, Count={r['tweet_count']})")
    db.close()

if __name__ == "__main__":
    test_latest_hashtags()
