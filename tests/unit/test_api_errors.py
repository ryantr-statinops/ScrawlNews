import sqlite3
from unittest.mock import patch

import pytest
import redis
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import config
from src.config import settings
from src.utils.errors import (
    ConfigError,
    MessengerError,
    NotFoundError,
    ScrawlerError,
    ScrawlError,
    SynthesizerError,
)


@pytest.mark.parametrize(
    "error_type,status",
    [
        (ScrawlError, 500),
        (NotFoundError, 404),
        (ConfigError, 400),
        (ScrawlerError, 502),
        (SynthesizerError, 502),
        (MessengerError, 502),
    ],
)
@pytest.mark.parametrize("retryable", [False, True])
def test_sanitized_domain_http_mapping(error_type, status, retryable):
    error = error_type("secret-token database-path provider-body", retryable=retryable)
    if retryable and status == 502:
        status = 503
    with patch("src.api.routes.summaries.SummaryRepository", side_effect=error):
        response = TestClient(app).get("/api/summaries/private-id")
    assert response.status_code == status
    assert response.json() == {"error": error.public_message}
    assert "secret-token" not in response.text
    assert "private-id" not in response.text


@pytest.mark.parametrize("error", [sqlite3.OperationalError("secret database"), TypeError("bug")])
def test_unexpected_http_error_is_not_a_domain_fallback(error):
    with patch("src.api.routes.summaries.SummaryRepository", side_effect=error):
        with pytest.raises(type(error)) as caught:
            TestClient(app).get("/api/summaries/id")
        response = TestClient(app, raise_server_exceptions=False).get("/api/summaries/id")
    assert caught.value is error
    assert response.status_code == 500
    assert response.text == "Internal Server Error"


@pytest.mark.parametrize(
    "payload",
    [
        {"fetch_limit": "invalid"},
        {"fetch_limit": None},
        {"fetch_limit": True},
        {"fetch_limit": 1.5},
        {"fetch_limit": 0},
        {"retention_days": -1},
        {"telegram_enabled": "invalid"},
        {"news_categories": ["tech"]},
    ],
)
def test_config_validation_precedes_all_writes(payload):
    response = TestClient(app).put("/api/config", json={"summary_lang": "en", **payload})
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid configuration"}
    assert config._config_repo.get_all() == {}
    assert config._config_repo.get_history() == []
    assert settings.summary_lang == "vi"


def test_config_notification_failure_preserves_saved_update():
    with patch("redis.from_url", side_effect=redis.ConnectionError("offline")):
        response = TestClient(app).put("/api/config", json={"fetch_limit": "25"})
    assert response.status_code == 200
    assert response.json() == {"updated": {"fetch_limit": "25"}}
    assert config._config_repo.get("fetch_limit") == "25"
    assert settings.fetch_limit == 25


@pytest.mark.parametrize(
    "method,error",
    [
        ("_config_repo.set", sqlite3.OperationalError("database failure")),
        ("_publish_config_change", TypeError("bug")),
    ],
)
def test_config_unexpected_errors_propagate(method, error):
    with patch(f"src.api.routes.config.{method}", side_effect=error):
        with pytest.raises(type(error)) as caught:
            TestClient(app).put("/api/config", json={"fetch_limit": 25})
    assert caught.value is error


def test_notification_programming_error_propagates():
    with patch("redis.from_url", side_effect=TypeError("bug")):
        with pytest.raises(TypeError, match="bug"):
            config._publish_config_change(["fetch_limit"])


@pytest.mark.parametrize("status", ["FAILURE", "RETRY"])
@pytest.mark.parametrize(
    "error,public",
    [
        (ScrawlerError("secret-token", retryable=True), "News source unavailable"),
        (sqlite3.OperationalError("private database path"), "Task failed"),
    ],
)
def test_failed_task_result_is_sanitized(status, error, public):
    with patch("src.worker.celery_app.celery_app.AsyncResult") as result:
        result.return_value.status = status
        result.return_value.result = error
        response = TestClient(app).get("/api/tasks/task-id")
    assert response.status_code == 200
    assert response.json() == {
        "task_id": "task-id",
        "status": status,
        "result": {"error": public},
    }


def test_health_database_error_is_sanitized():
    with patch("src.api.routes.health.ArticleRepository", side_effect=sqlite3.Error("secret")):
        response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["db"] == "unavailable"
    assert "secret" not in response.text
