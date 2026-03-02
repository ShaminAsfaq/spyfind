"""FastAPI application entry point."""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import init_db
from app.routes import router
from user_management_panel.routes import router as admin_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Spyfind",
    description="Twitter/X simulation for bot detection testing",
    version="1.0.0"
)

# Include API routes
app.include_router(router)
app.include_router(admin_router)

# Mount static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def read_root():
    """Serve the main frontend."""
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Spyfind API - Visit /docs for API documentation"}


@app.get("/docs", include_in_schema=False)
def get_docs():
    """Redirect to OpenAPI docs."""
    return FileResponse(path="/docs")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/admin")
def admin_panel():
    """Serve the admin user management panel."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "user_management_panel", "templates", "users.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Admin panel not found"}


@app.get("/admin/test")
def admin_test():
    """Serve the API test page."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "user_management_panel", "templates", "test_api.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Test page not found"}


@app.get("/profile/{user_id}")
def user_profile_page(user_id: int):
    """Serve the user profile page with tweets."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "user_management_panel", "templates", "profile.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Profile page template not found"}


@app.get("/admin/hashtags")
def admin_hashtags_page():
    """Serve the hashtag injection panel."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "user_management_panel", "templates", "hashtags.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Hashtag injection panel not found"}


@app.get("/admin/post-tweet")
def admin_post_tweet_page():
    """Serve the post tweet panel."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "user_management_panel", "templates", "post_tweet.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Post tweet panel not found"}


@app.get("/admin/bot-detector")
def admin_bot_detector_page():
    """Serve the bot detector panel."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "user_management_panel", "templates", "bot_detector.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Bot detector panel not found"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
