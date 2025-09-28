from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import sys
from pathlib import Path

# Add the parent directory to the path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from .api.routes import router
    from .database import engine, Base, close_db_connections
except ImportError:
    # If relative imports fail, try absolute imports
    from app.api.routes import router
    from app.database import engine, Base, close_db_connections

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="URL Shortener API",
    description="High-performance URL Shortener API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "URL Shortener API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Database tables creation failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    await close_db_connections()
    logger.info("Database connections closed")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "url_shortener"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )