# User Management Panel

A comprehensive web-based interface for managing users in the Spyfind system.

## Features

✅ **View All Users** - Browse through all users with pagination
✅ **Search Users** - Search by username or display name
✅ **Create Users** - Add new users with complete profile information
✅ **Edit Users** - Update existing user details
✅ **Delete Users** - Remove users from the system
✅ **User Statistics** - View total user count and displayed count
✅ **Responsive Design** - Beautiful gradient UI with smooth interactions

## File Structure

```
user_management_panel/
├── __init__.py           # Package initialization
├── routes.py             # FastAPI routes for user CRUD operations
├── templates/
│   └── users.html        # Frontend HTML with embedded CSS and JavaScript
└── README.md             # This file
```

## API Endpoints

All endpoints are prefixed with `/admin/users`:

- **GET** `/admin/users/` - Get all users (with pagination and search)
  - Query params: `skip`, `limit`, `search`
- **GET** `/admin/users/count` - Get total count of users
- **GET** `/admin/users/{user_id}` - Get specific user by ID
- **POST** `/admin/users/` - Create a new user
- **PUT** `/admin/users/{user_id}` - Update an existing user
- **DELETE** `/admin/users/{user_id}` - Delete a user

## Access

Once the FastAPI server is running, access the panel at:

```
http://localhost:8000/admin
```

## Usage

### View Users
- Users are automatically loaded when you visit the page
- Navigate between pages using Previous/Next buttons
- Default page size: 50 users per page

### Search Users
- Type in the search box to filter by username or display name
- Search is debounced (500ms delay) for better performance

### Create New User
1. Click the "➕ Add New User" button
2. Fill in the required fields (username, display name)
3. Optionally fill in other fields (bio, location, counts, etc.)
4. Click "Save User"

### Edit User
1. Click the "✏️ Edit" button on any user row
2. Modify the fields as needed
3. Click "Save User"

### Delete User
1. Click the "🗑️ Delete" button on any user row
2. Confirm the deletion in the popup
3. User will be permanently removed

## Technical Details

### Backend (FastAPI)
- Uses SQLAlchemy ORM for database operations
- Implements proper error handling and validation
- Returns appropriate HTTP status codes
- Supports query parameters for filtering and pagination

### Frontend (HTML/CSS/JavaScript)
- Vanilla JavaScript (no frameworks required)
- Responsive design with gradient styling
- Real-time search with debouncing
- Modal forms for create/edit operations
- Success/error message notifications

## Integration

The panel is automatically integrated into the main FastAPI application via:

```python
from user_management_panel.routes import router as admin_router
app.include_router(admin_router)
```

## Notes

- Username must be unique
- Display name is required
- All count fields default to 0 if not specified
- Colors use hex format (#rrggbb)
- Deleting a user will cascade delete their tweets, reposts, and comments
