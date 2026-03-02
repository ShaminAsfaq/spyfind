import sys
import os
import joblib
import pandas as pd
import traceback

# --- SET USERNAME HERE ---
username_to_check = "nbcwashington"
# -------------------------

# Add the project root to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Force absolute path for database
DB_PATH = os.path.join(PROJECT_ROOT, 'spyfind.db')
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

from app.database import SessionLocal
from app.models import User, BotDetection

MODEL_PATH = os.path.join(PROJECT_ROOT, 'model', 'bot_detector.pkl')

def calculate_features(user):
    """
    Calculate the 5 required features for the model:
    1. statuses_count: Total posts (Tweets) published.
    2. followers_count: Total users following this account.
    3. friends_count: Total accounts followed by user.
    4. reputation: Followers / (Followers + Friends + 1).
    5. post_to_follower_ratio: Statuses / (Followers + 1).
    """
    statuses = user.posts_count or 0
    followers = user.followers_count or 0
    friends = user.following_count or 0
    
    reputation = followers / (followers + friends + 1)
    post_to_follower_ratio = statuses / (followers + 1)
    
    return [statuses, followers, friends, reputation, post_to_follower_ratio]

import traceback

def run_single_prediction():
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        return

    db = SessionLocal()
    try:
        # Fetch the specific user
        user = db.query(User).filter(User.username == username_to_check).first()
        
        if not user:
            print(f"❌ User '@{username_to_check}' not found in the database.")
            return

        # Fetch ground truth
        bot_entry = db.query(BotDetection).filter(BotDetection.user_id == user.id).first()
        ground_truth = bot_entry.is_bot if bot_entry else None

        print(f"Found user: {user.display_name} (@{user.username})")
        print("Loading ML model...")
        try:
            model = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Error loading model: {e}")
            traceback.print_exc()
            return
        
        # Calculate features
        features = calculate_features(user)
        feature_names = [
            'statuses_count', 'followers_count', 'friends_count', 
            'reputation', 'post_to_follower_ratio'
        ]
        
        # Create DataFrame for model input
        df = pd.DataFrame([features], columns=feature_names)
        
        print("\n" + "="*60)
        print(f"FEATURE CALCULATION FOR @{user.username}")
        print("-" * 60)
        for name, value in zip(feature_names, features):
            if isinstance(value, float):
                print(f"{name:25}: {value:.4f}")
            else:
                print(f"{name:25}: {value}")
        
        # Run prediction
        try:
            prediction = bool(model.predict(df)[0])
            status = "🤖 BOT" if prediction else "👤 HUMAN"
            print("-" * 60)
            print(f"FINAL PREDICTION: {status}")

            # Ground Truth Comparison
            if ground_truth is not None:
                is_correct = (prediction == ground_truth)
                truth_status = "🤖 BOT" if ground_truth else "👤 HUMAN"
                print(f"GROUND TRUTH    : {truth_status}")
                print(f"VERDICT         : {'✅ CORRECT' if is_correct else '❌ FALSE'}")
            else:
                print("GROUND TRUTH    : Data not available for this user.")

        except Exception as e:
            print(f"Error during model prediction: {e}")
            traceback.print_exc()
        
        print("="*60)
        print("\nNOTE: This script is READ-ONLY. No database changes were made.")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_single_prediction()
