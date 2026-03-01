# How to Run the User Management Panel

## Prerequisites

Make sure you have Python installed and all dependencies are installed:

```bash
cd D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind
pip install -r requirements.txt
```

## Starting the Server

Run the FastAPI server:

```bash
cd D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or alternatively:

```bash
cd D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind
python app/main.py
```

## Accessing the Panel

Once the server is running, open your browser and go to:

**User Management Panel:**
```
http://localhost:8000/admin
```

**API Documentation:**
```
http://localhost:8000/docs
```

**Main App:**
```
http://localhost:8000/
```

## Quick Test

To verify everything is working:

1. Start the server (see above)
2. Visit http://localhost:8000/admin
3. You should see the User Management Panel with all users loaded
4. Try searching for a user
5. Try creating a new user
6. Try editing an existing user

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, you can change it:
```bash
python -m uvicorn app.main:app --reload --port 8001
```
Then access at: http://localhost:8001/admin

### Module Not Found Errors
Make sure all dependencies are installed:
```bash
pip install fastapi uvicorn sqlalchemy python-dateutil pydantic
```

### Database Not Found
The database will be automatically created when you run the app for the first time. Make sure the `spyfind.db` file exists in the project root.

## Expected Behavior

- **Loading**: Users should load within 1-2 seconds
- **Search**: Search results appear after 500ms of typing
- **Pagination**: 50 users per page by default
- **CRUD Operations**: All create, read, update, delete operations should work smoothly
