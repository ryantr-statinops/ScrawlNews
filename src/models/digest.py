from dataclasses import dataclass
from datetime import datetime


@dataclass
class Digest:
    id: str
    category: str
    title: str
    digest_text: str
    article_count: int
    model_used: str
    status: str = "ready"
    error: str | None = None
    created_at: datetime | None = None
