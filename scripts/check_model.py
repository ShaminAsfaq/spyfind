import joblib
import numpy as np
import os

def check_model():
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(PROJECT_ROOT, 'model', 'bot_detector.pkl')
    try:
        model = joblib.load(model_path)
        
        print(f"Model type: {type(model)}")
        if hasattr(model, 'n_features_in_'):
            print(f"Number of features expected: {model.n_features_in_}")
        
        if hasattr(model, 'feature_names_in_'):
            print(f"Feature names: {model.feature_names_in_}")
        
    except Exception as e:
        print(f"Error loading model: {e}")

if __name__ == "__main__":
    check_model()
