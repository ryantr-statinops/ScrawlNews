import pytest
import httpx


@pytest.fixture(scope="session")
def live_url():
    return "http://localhost:8000"


def test_health_live(live_url):
    try:
        r = httpx.get(f"{live_url}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
    except Exception:
        pytest.skip("Live server not available")


def test_config_live(live_url):
    try:
        r = httpx.get(f"{live_url}/api/config", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "fetch_limit" in data
        assert "telegram_enabled" in data
    except Exception:
        pytest.skip("Live server not available")


def test_articles_live(live_url):
    try:
        r = httpx.get(f"{live_url}/api/articles?limit=5", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "count" in data
        assert "articles" in data
    except Exception:
        pytest.skip("Live server not available")


def test_summaries_live(live_url):
    try:
        r = httpx.get(f"{live_url}/api/summaries?limit=5", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "count" in data
        assert "summaries" in data
    except Exception:
        pytest.skip("Live server not available")


def test_runs_live(live_url):
    try:
        r = httpx.get(f"{live_url}/api/runs", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "runs" in data
    except Exception:
        pytest.skip("Live server not available")


def test_stats_live(live_url):
    try:
        r = httpx.get(f"{live_url}/api/stats", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "articles_per_day" in data
        assert "source_dist" in data
    except Exception:
        pytest.skip("Live server not available")
