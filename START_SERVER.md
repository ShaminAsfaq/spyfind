# How to Start the Spyfind Server

## Step 1: Install Dependencies

```bash
cd D:\KASTIRO\SpyfindFYP-main\SpyfindFYP-main\spyfind
pip install -r requirements.txt
```

If requirements.txt is missing some packages, install manually:
```bash
pip install fastapi uvicorn sqlalchemy python-dateutil pydantic
```

## Step 2: Start the Server

### Option A: Using uvicorn directly
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option B: Using the main.py file
```bash
python app/main.py
```

## Step 3: Access the Application

Once the server is running, you should see output like:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Then open your browser and go to:

- **Main App**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## Troubleshooting

### "Error loading users: Failed to load users"

This error means the JavaScript cannot connect to the API. Check:

1. **Is the server running?** - Look for the uvicorn output in terminal
2. **Is it on the right port?** - Default is 8000
3. **Check browser console** - Press F12 and look at Console tab for detailed errors
4. **Check Network tab** - Press F12, go to Network tab, reload page, look for failed requests

### Common Issues

**Module not found errors**: Install dependencies
```bash
pip install fastapi uvicorn sqlalchemy python-dateutil pydantic
```

**Port already in use**: Change the port
```bash
python -m uvicorn app.main:app --reload --port 8001
```

**Database errors**: Make sure spyfind.db exists and has users
```bash
python -c "import sqlite3; conn = sqlite3.connect('spyfind.db'); c = conn.cursor(); c.execute('SELECT COUNT(*) FROM users'); print(f'Users: {c.fetchone()[0]}'); conn.close()"
```

## Verify Everything is Working

1. Start server (see Step 2)
2. Open http://localhost:8000/docs
3. Try the `/admin/users/` endpoint with default parameters
4. You should see a JSON response with user data
5. If that works, go to http://localhost:8000/admin
6. The user management panel should load with all users displayed
