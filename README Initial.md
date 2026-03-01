# Spyfind - Twitter/X Simulation for Bot Detection Testing

A lightweight web application designed to simulate Twitter/X functionality, specifically built for testing and developing bot-detection systems.

## Features

- **Hashtag Search**: Search for tweets by hashtag
- **User Profiles**: View detailed user metadata and account information
- **Dynamic Hashtag Creation**: Automatically creates new hashtags when tweets contain them
- **Many-to-Many Relationships**: Proper handling of tweets with multiple hashtags
- **RESTful API**: JSON endpoints for programmatic access
- **Clean Architecture**: Separated backend and frontend layers

## Project Structure

```
spyfind/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas for API
│   ├── crud.py              # CRUD operations
│   └── routes.py            # API endpoints
├── static/
│   └── index.html           # Frontend UI
├── scripts/
│   └── seed.py              # Sample data seeding
├── requirements.txt         # Python dependencies
└── spyfind.db              # SQLite database (created on first run)
```

## Installation

1. Clone or extract the project
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Seed initial data** (optional):
   ```bash
   python scripts/seed.py
   ```

2. **Start the server**:
   ```bash
   python app/main.py
   ```
   The application will be available at `http://localhost:8000`

## API Endpoints

### Hashtags
- `GET /api/hashtags` - List all hashtags
- `GET /api/hashtags/{hashtag_id}` - Get hashtag details with tweets
- `GET /api/hashtags/search/{query}` - Search hashtags by name

### Tweets
- `GET /api/tweets` - List all tweets
- `GET /api/tweets/{tweet_id}` - Get tweet details
- `POST /api/tweets` - Create a new tweet
- `POST /api/tweets/{tweet_id}/like` - Like a tweet

### Users
- `GET /api/users` - List all users
- `GET /api/users/{user_id}` - Get user profile details

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (easily replaceable with PostgreSQL)
- **ORM**: SQLAlchemy
- **Frontend**: HTML5 + CSS + Vanilla JavaScript

## Future Expansions

- External bot-detection module integration
- Analytics endpoints for bot behavior analysis
- Tweet sentiment analysis
- User activity patterns tracking
- CSV/JSON data import functionality
