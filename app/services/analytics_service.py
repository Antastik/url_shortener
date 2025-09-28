from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import URL, Analytics
from ..schemas import AnalyticsResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    async def record_click(
        self, 
        db: AsyncSession, 
        short_code: str, 
        ip_address: str, 
        user_agent: str, 
        referer: str = None
    ) -> None:
        """Record a click for analytics"""
        try:
            analytics = Analytics(
                short_code=short_code,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer
            )
            db.add(analytics)
            await db.commit()
        except Exception as e:
            logger.error(f"Error recording analytics: {str(e)}")
            await db.rollback()
            raise
    
    async def get_analytics(self, db: AsyncSession, short_code: str) -> AnalyticsResponse:
        """Get analytics data for a short URL"""
        try:
            # Get URL record
            url_result = await db.execute(
                select(URL).where(URL.short_code == short_code)
            )
            url_record = url_result.scalar_one_or_none()
            
            if not url_record:
                raise ValueError("URL not found")
            
            # Get analytics data
            analytics_result = await db.execute(
                select(Analytics).where(Analytics.short_code == short_code)
            )
            analytics_records = analytics_result.scalars().all()
            
            # Get recent clicks (last 10)
            recent_clicks = [
                {
                    "timestamp": record.timestamp,
                    "ip_address": record.ip_address,
                    "user_agent": record.user_agent,
                    "referer": record.referer
                }
                for record in analytics_records[-10:]  # Last 10 clicks
            ]
            
            return AnalyticsResponse(
                short_code=short_code,
                total_clicks=len(analytics_records),
                recent_clicks=recent_clicks,
                created_at=url_record.created_at
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise ValueError(f"Failed to get analytics: {str(e)}")
    
    async def get_click_stats(self, db: AsyncSession, short_code: str) -> dict:
        """Get click statistics for a short URL"""
        try:
            # Get total clicks
            total_result = await db.execute(
                select(func.count(Analytics.id)).where(Analytics.short_code == short_code)
            )
            total_clicks = total_result.scalar() or 0
            
            # Get clicks by day (last 30 days)
            thirty_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            thirty_days_ago = thirty_days_ago.replace(day=thirty_days_ago.day - 30)
            
            daily_result = await db.execute(
                select(
                    func.date(Analytics.timestamp).label('date'),
                    func.count(Analytics.id).label('clicks')
                )
                .where(
                    Analytics.short_code == short_code,
                    Analytics.timestamp >= thirty_days_ago
                )
                .group_by(func.date(Analytics.timestamp))
                .order_by(func.date(Analytics.timestamp))
            )
            daily_stats = daily_result.fetchall()
            
            return {
                "total_clicks": total_clicks,
                "daily_clicks": [
                    {"date": str(stat.date), "clicks": stat.clicks} 
                    for stat in daily_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting click stats: {str(e)}")
            raise ValueError(f"Failed to get click stats: {str(e)}")
