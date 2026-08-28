import json
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.article import Article
from src.models.summary import Summary
from src.models.run import PipelineRun
from src.repositories.article_repo import ArticleRepository
from src.repositories.summary_repo import SummaryRepository
from src.repositories.run_repo import PipelineRunRepository
from src.services.scrawler import ScrawlerService
from src.services.synthesizer import SynthesizerService
from src.services.messenger import MessengerService


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str):
    path = FIXTURES_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_articles():
    data = load_fixture("sample_articles.json")
    return [Article(**a) for a in data]


@pytest.fixture
def sample_rss_xml():
    return (FIXTURES_DIR / "sample_rss.xml").read_text(encoding="utf-8")


@pytest.fixture
def sample_html():
    return (FIXTURES_DIR / "sample_html.html").read_text(encoding="utf-8")


@pytest.fixture
def mock_llm_response():
    data = load_fixture("llm_responses.json")
    return data[0]


@pytest.fixture
def mock_http_client():
    client = AsyncMock()
    with patch("httpx.AsyncClient") as mock:
        mock.return_value.__aenter__.return_value = client
        yield client


@pytest.fixture
def mock_openai():
    with patch("openai.AsyncOpenAI") as mock:
        yield mock.return_value


@pytest.fixture
def mock_telegram_bot():
    bot = AsyncMock()
    with patch("telegram.Bot") as mock:
        mock.return_value = bot
        yield bot


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    yield str(db_path)


@pytest.fixture
def article_repo(temp_db):
    return ArticleRepository(f"sqlite:///{temp_db}")


@pytest.fixture
def summary_repo(temp_db):
    return SummaryRepository(f"sqlite:///{temp_db}")


@pytest.fixture
def run_repo(temp_db):
    return PipelineRunRepository(f"sqlite:///{temp_db}")


@pytest.fixture
def scrawler_service():
    return ScrawlerService()


@pytest.fixture
def synthesizer_service():
    return SynthesizerService()


@pytest.fixture
def messenger_service():
    return MessengerService()
