from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsSource:
    id: str
    name: str
    url: str
    category: str | None = None
    country: str = "VN"
    city: str | None = None
    enabled: int = 1
    last_status: str | None = None
    last_error: str | None = None
    last_checked_at: datetime | None = None
    created_at: datetime | None = None
