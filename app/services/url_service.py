from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import URL
from ..utils.url_generator import URLGenerator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class URLService:
    def __init__(self):
        self.url_generator = URLGenerator()
    
    async def create_short_url(
        self, 
        db: AsyncSession, 
        original_url: str, 
        custom_short_code: str = None
    ) -> URL:
        """Create a new short URL"""
        try:
            # Check if custom code is provided and valid
            if custom_short_code:
                if not self.url_generator.is_valid_custom_code(custom_short_code):
                    raise ValueError(
                        "Custom code must be 3-20 characters and contain only letters, numbers, hyphens, and underscores"
                    )
                
                # Check if custom code already exists
                existing_url = await db.execute(
                    select(URL).where(URL.short_code == custom_short_code)
                )
                if existing_url.scalar_one_or_none():
                    raise ValueError("Custom code already exists")
                
                short_code = custom_short_code
                is_custom = True
            else:
                # Generate random short code
                short_code = self.url_generator.generate_short_code(original_url)
                is_custom = False
                
                # Ensure uniqueness
                max_attempts = 10
                attempts = 0
                while attempts < max_attempts:
                    existing_url = await db.execute(
                        select(URL).where(URL.short_code == short_code)
                    )
                    if not existing_url.scalar_one_or_none():
                        break
                    short_code = self.url_generator.generate_short_code(original_url)
                    attempts += 1
                
                if attempts >= max_attempts:
                    raise ValueError("Unable to generate unique short code")

            # Create new URL record
            new_url = URL(
                original_url=original_url,
                short_code=short_code,
                custom_code=is_custom
            )
            
            db.add(new_url)
            await db.commit()
            await db.refresh(new_url)
            
            return new_url
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            await db.rollback()
            raise ValueError(f"Failed to create short URL: {str(e)}")
    
    async def get_original_url(self, db: AsyncSession, short_code: str) -> str:
        """Get the original URL for a short code"""
        try:
            result = await db.execute(
                select(URL).where(
                    URL.short_code == short_code,
                    URL.is_active == True
                )
            )
            url_record = result.scalar_one_or_none()
            
            if not url_record:
                return None
            
            return url_record.original_url
            
        except Exception as e:
            logger.error(f"Error getting original URL: {str(e)}")
            return None
    
    async def deactivate_url(self, db: AsyncSession, short_code: str) -> bool:
        """Deactivate a short URL"""
        try:
            result = await db.execute(
                select(URL).where(URL.short_code == short_code)
            )
            url_record = result.scalar_one_or_none()
            
            if not url_record:
                return False
            
            url_record.is_active = False
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating URL: {str(e)}")
            await db.rollback()
            return False
