from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    id: str
    url: str
    title: str
    source: str | None = None
    raw_html: str | None = None
    content: str | None = None
    fetched_at: datetime | None = None
    summarized: int = 0
