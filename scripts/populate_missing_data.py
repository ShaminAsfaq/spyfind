
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User

def populate_missing():
    db = SessionLocal()
    users = db.query(User).all()
    
    profile_colors = [
        "#1da1f2", "#e74c3c", "#3498db", "#9b59b6", "#2ecc71",
        "#f39c12", "#34495e", "#e67e22", "#1abc9c", "#d35400",
        "#c0392b", "#8e44ad", "#27ae60", "#2980b9", "#16a085"
    ]
    
    banner_colors = [
        "#667eea", "#764ba2", "#2c3e50", "#000000", "#556270", 
        "#4ECDC4", "#FF6B6B", "#C7F464", "#556270", "#1da1f2"
    ]

    banner_images = [
        "https://images.unsplash.com/photo-1557683316-973673baf926",
        "https://images.unsplash.com/photo-1504333638930-c8787321eba0",
        "https://images.unsplash.com/photo-1519681393784-d120267933ba",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b",
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
        "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
        "https://images.unsplash.com/photo-1472214103451-9374bd1c798e",
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef",
        "https://images.unsplash.com/photo-1434725039720-abb26e22ebe8",
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23",
        "https://images.unsplash.com/photo-1532274402911-5a3b027c55b9",
        "https://images.unsplash.com/photo-1493246507139-91e8bef99c02",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1",
        "https://images.unsplash.com/photo-1418065460487-3e41a6c84dc5",
        "https://images.unsplash.com/photo-1426604966848-d7adac402bff",
        "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d",
        "https://images.unsplash.com/photo-1470770841072-f978cf4d019e"
    ]
    
    avatar_styles = ['avataaars', 'bottts', 'adventurer', 'lorelei', 'pixel-art', 'fun-emoji']
    
    count = 0
    for u in users:
        # Update profile color if default or empty
        if not u.profile_color or u.profile_color in ["#1da1f2", ""]:
            u.profile_color = random.choice(profile_colors)
            
        # Update banner color if default or empty
        if not u.banner_color or u.banner_color in ["#ffffff", ""]:
            u.banner_color = random.choice(banner_colors)
            
        # Add a placeholder image if missing
        if not u.profile_image_url:
            style = random.choice(avatar_styles)
            u.profile_image_url = f"https://api.dicebear.com/7.x/{style}/svg?seed={u.username}"
        
        # Add random banner image
        if not u.profile_banner_url:
            u.profile_banner_url = random.choice(banner_images)
            
        count += 1
    
    db.commit()
    print(f"Updated data for {count} users.")
    db.close()

if __name__ == "__main__":
    populate_missing()
