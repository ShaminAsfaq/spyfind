"""FastAPI application entry point (API ONLY)."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.database import init_db
from app.routes import router
from user_management_panel.routes import router as admin_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Spyfind API",
    description="Twitter/X simulation for bot detection testing - Backend API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(admin_router)


@app.get("/")
def read_root():
    """Redirect to OpenAPI docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
