import sqlite3

conn = sqlite3.connect(r'D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind\spyfind.db')
cursor = conn.cursor()

# Count total users
cursor.execute('SELECT COUNT(*) FROM users')
total = cursor.fetchone()[0]
print(f'Total users in database: {total}')

# Show sample data
cursor.execute('SELECT id, username, display_name, followers_count, created_at FROM users LIMIT 5')
print('\nSample data:')
print('-' * 80)
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Username: {row[1]}, Name: {row[2]}, Followers: {row[3]}, Created: {row[4]}")

conn.close()
