from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas import URLCreate, URLResponse, AnalyticsResponse
from ..services.url_service import URLService
from ..services.analytics_service import AnalyticsService
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
url_service = URLService()
analytics_service = AnalyticsService()

# Railway provides RAILWAY_STATIC_URL, or use custom domain
BASE_URL = os.getenv("RAILWAY_STATIC_URL") or os.getenv("BASE_URL", "http://localhost:8000")

@router.post("/shorten", response_model=URLResponse)
async def create_short_url(
    url_data: URLCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Rate limiting based on IP (simple version)
        client_ip = request.client.host
        logger.info(f"Shortening URL for IP: {client_ip}")
        
        db_url = await url_service.create_short_url(
            db, 
            str(url_data.url), 
            url_data.custom_short_code
        )
        
        short_url = f"{BASE_URL.rstrip('/')}/{db_url.short_code}"
        
        return URLResponse(
            short_url=short_url,
            original_url=db_url.original_url,
            short_code=db_url.short_code,
            created_at=db_url.created_at
        )
    except ValueError as e:
        logger.warning(f"URL shortening error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        original_url = await url_service.get_original_url(db, short_code)
        
        if not original_url:
            raise HTTPException(status_code=404, detail="Short URL not found")
        
        # Record analytics asynchronously (fire and forget)
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer")
        
        try:
            await analytics_service.record_click(db, short_code, client_ip, user_agent, referer)
        except Exception as analytics_error:
            logger.warning(f"Analytics recording failed: {str(analytics_error)}")
        
        return RedirectResponse(url=original_url, status_code=301)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redirect error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/analytics/{short_code}")
async def get_analytics(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        analytics_data = await analytics_service.get_analytics(db, short_code)
        return analytics_data
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve analytics")

@router.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "component": "api"}