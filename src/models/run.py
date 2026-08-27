from dataclasses import dataclass
from datetime import datetime


@dataclass
class PipelineRun:
    id: str
    status: str  # pending|running|success|failed
    task_id: str | None = None
    articles_fetched: int = 0
    summaries_generated: int = 0
    telegram_sent: int = 0
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
