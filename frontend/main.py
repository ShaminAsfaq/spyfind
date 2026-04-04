"""FastAPI frontend server."""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Spyfind Frontend")

# Define base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Serve static files (for any future static assets)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    """Serve the main landing page."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/newsfeed")
def newsfeed():
    """Serve the newsfeed page."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "newsfeed.html"))


@app.get("/admin")
def admin_panel():
    """Serve the admin user management panel."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "users.html"))


@app.get("/admin/test")
def admin_test():
    """Serve the API test page."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "test_api.html"))


@app.get("/profile/{user_id}")
def user_profile(user_id: str):
    """Serve the user profile page."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "profile.html"))


@app.get("/admin/hashtags")
def admin_hashtags():
    """Serve the hashtag injection panel."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "hashtags.html"))


@app.get("/admin/post-tweet")
def admin_post_tweet():
    """Serve the post tweet panel."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "post_tweet.html"))


@app.get("/admin/bot-detector")
def admin_bot_detector():
    """Serve the bot detector panel."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "bot_detector.html"))


@app.get("/demonstration")
def demonstration_panel():
    """Serve the demonstration panel."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "demonstration.html"))


@app.get("/hashtag-analyzer")
def hashtag_analyzer_panel():
    """Serve the hashtag analyzer panel."""
    return FileResponse(os.path.join(TEMPLATES_DIR, "hashtag_analyzer.html"))


if __name__ == "__main__":
    print("Spyfind Frontend running at http://localhost:3000")
    print("Pointed to Backend at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=3000)
