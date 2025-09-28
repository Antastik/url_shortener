from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    url: HttpUrl
    custom_short_code: Optional[str] = None

class URLResponse(BaseModel):
    short_url: str
    original_url: str
    short_code: str
    created_at: datetime

class AnalyticsResponse(BaseModel):
    short_code: str
    total_clicks: int
    recent_clicks: list
    created_at: datetime