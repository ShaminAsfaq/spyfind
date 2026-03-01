"""
Import users from CSV file into Spyfind database.

CSV Format:
username,display_name,bio,location,url,followers_count,following_count,posts_count,likes_count,listed_count,profile_color,banner_color

Example:
john_doe,John Doe,Software Engineer,San Francisco,https://johndoe.com,1500,800,250,5000,50,#1da1f2,#ffffff
"""
import sys
import os
import csv
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User


def generate_random_color():
    """Generate random profile/banner color if not provided."""
    profile_colors = [
        "#1da1f2", "#e74c3c", "#3498db", "#9b59b6", "#2ecc71",
        "#f39c12", "#34495e", "#e67e22", "#1abc9c", "#d35400"
    ]
    banner_colors = [
        "#ffffff", "#f0f0f0", "#e8f5ff", "#fff3e0", "#f3e5f5",
        "#e8f8f5", "#fce4ec", "#e0f2f1"
    ]
    return random.choice(profile_colors), random.choice(banner_colors)


def import_users_from_csv(csv_file_path):
    """Import users from CSV file."""
    db = SessionLocal()

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            users_created = 0
            users_skipped = 0

            for row in reader:
                # Check if user already exists
                existing_user = db.query(User).filter(User.username == row['username']).first()
                if existing_user:
                    print(f"⚠️  User '{row['username']}' already exists, skipping...")
                    users_skipped += 1
                    continue

                # Generate colors if not provided
                profile_color = row.get('profile_color', '').strip()
                banner_color = row.get('banner_color', '').strip()
                if not profile_color or not banner_color:
                    profile_color, banner_color = generate_random_color()

                # Create user
                user = User(
                    username=row['username'].strip(),
                    display_name=row.get('display_name', row['username']).strip(),
                    bio=row.get('bio', '').strip(),
                    location=row.get('location', '').strip(),
                    url=row.get('url', '').strip(),
                    followers_count=int(row.get('followers_count', 0) or 0),
                    following_count=int(row.get('following_count', 0) or 0),
                    posts_count=int(row.get('posts_count', 0) or 0),
                    likes_count=int(row.get('likes_count', 0) or 0),
                    listed_count=int(row.get('listed_count', 0) or 0),
                    retweets_count=int(row.get('retweets_count', 0) or 0),
                    profile_color=profile_color,
                    banner_color=banner_color,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365*3))
                )

                db.add(user)
                users_created += 1
                print(f"✅ Created user: {user.username} ({user.display_name})")

            db.commit()

            print("\n" + "="*60)
            print(f"Import completed!")
            print(f"  ✅ Users created: {users_created}")
            print(f"  ⚠️  Users skipped: {users_skipped}")
            print("="*60)

    except FileNotFoundError:
        print(f"❌ Error: File '{csv_file_path}' not found!")
    except Exception as e:
        print(f"❌ Error importing users: {e}")
        db.rollback()
    finally:
        db.close()


def export_users_to_csv(output_file_path):
    """Export all users to CSV file."""
    db = SessionLocal()

    try:
        users = db.query(User).all()

        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'username', 'display_name', 'bio', 'location', 'url',
                'followers_count', 'following_count', 'posts_count', 'likes_count',
                'listed_count', 'retweets_count', 'profile_color', 'banner_color',
                'created_at'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for user in users:
                writer.writerow({
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'bio': user.bio,
                    'location': user.location,
                    'url': user.url,
                    'followers_count': user.followers_count,
                    'following_count': user.following_count,
                    'posts_count': user.posts_count,
                    'likes_count': user.likes_count,
                    'listed_count': user.listed_count,
                    'retweets_count': user.retweets_count,
                    'profile_color': user.profile_color,
                    'banner_color': user.banner_color,
                    'created_at': user.created_at
                })

        print(f"✅ Exported {len(users)} users to '{output_file_path}'")

    except Exception as e:
        print(f"❌ Error exporting users: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Import: python import_users_from_csv.py import <csv_file>")
        print("  Export: python import_users_from_csv.py export <output_file>")
        print("\nExample:")
        print("  python import_users_from_csv.py import users.csv")
        print("  python import_users_from_csv.py export users_backup.csv")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "import":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide CSV file path")
            print("Usage: python import_users_from_csv.py import <csv_file>")
            sys.exit(1)
        csv_file = sys.argv[2]
        import_users_from_csv(csv_file)

    elif command == "export":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide output file path")
            print("Usage: python import_users_from_csv.py export <output_file>")
            sys.exit(1)
        output_file = sys.argv[2]
        export_users_to_csv(output_file)

    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'import' or 'export'")
        sys.exit(1)
