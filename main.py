"""
FastAPI application for WattWise Admin Portal.

This is the main entry point for the backend API.
Reference Frontend: https://meter-zen-portal.lovable.app

Features:
- Admin registration and login
- JWT-based authentication
- Password hashing with bcrypt
- OTP-based password reset
- Role-based access control
- SQLAlchemy ORM integration
"""

from fastapi import FastAPI, Depends
from utils.dependencies import get_current_admin
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.exc import SQLAlchemyError

# Import routes
from routes.admin_auth import router as admin_auth_router
from routes.users import router as users_router
from routes.complaints import router as complaints_router
from routes.revenue_routes import router as revenue_router
from routes.sms_routes import router as sms_router
from routes.dashboard_routes import router as dashboard_router
from routes.settings_routes import router as settings_router
from routes.reference_routes import router as reference_router

# Import database and models to ensure tables are created
from config.database import engine, Base
import models.admin  # noqa: F401
import models.user   # noqa: F401
import models.complaint  # noqa: F401
import models.transaction  # noqa: F401
import models.sms  # noqa: F401
import models.settings  # noqa: F401
import models.reference_data  # noqa: F401

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WattWise Admin Portal API",
    description="Authentication and admin management API for WattWise Admin Portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (Cross-Origin Resource Sharing)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite development
    "https://meter-zen-portal.lovable.app",  # Production frontend
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add optional extra origins from environment variable (comma-separated)
import os
extra_origins = os.getenv("ALLOWED_ORIGINS")
if extra_origins:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in extra_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create all database tables on application startup."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully.")
    except SQLAlchemyError as exc:
        logger.error("Database initialization skipped: %s", str(exc))
        logger.error("Check your DATABASE_URL/DB_URI in .env and rerun migrations.")


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "service": "WattWise Admin Portal API",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": "Welcome to WattWise Admin Portal API",
        "documentation": "/docs",
        "api_version": "1.0.0",
        "endpoints": {
            "authentication": "/docs#/Admin%20Authentication",
            "health": "/health"
        }
    }


# Include routers
app.include_router(admin_auth_router)
app.include_router(users_router, dependencies=[Depends(get_current_admin)])
app.include_router(complaints_router, dependencies=[Depends(get_current_admin)])
app.include_router(revenue_router, dependencies=[Depends(get_current_admin)])
app.include_router(sms_router, dependencies=[Depends(get_current_admin)])
app.include_router(dashboard_router, dependencies=[Depends(get_current_admin)])
app.include_router(settings_router, dependencies=[Depends(get_current_admin)])
app.include_router(reference_router, dependencies=[Depends(get_current_admin)])


# Global exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for all unhandled errors.

    Args:
        request: Request object
        exc: Exception object

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if str(exc) else "Unknown error"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
