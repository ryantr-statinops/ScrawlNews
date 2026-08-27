from dataclasses import dataclass
from datetime import datetime


@dataclass
class Summary:
    id: str
    article_id: str
    summary_text: str
    model_used: str
    created_at: datetime | None = None
