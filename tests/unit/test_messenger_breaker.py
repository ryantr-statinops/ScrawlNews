import pytest

from src.models.summary import Summary
from src.services.messenger import MessengerService, _telegram_breaker
from src.utils.errors import ConfigError, MessengerError
from src.config import settings


@pytest.fixture
def messenger():
    svc = MessengerService()
    _telegram_breaker.reset()
    yield svc
    _telegram_breaker.reset()


def test_blocked_when_breaker_open(messenger, monkeypatch):
    monkeypatch.setattr(settings, "telegram_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "token")
    monkeypatch.setattr(settings, "telegram_chat_id", "chat")
    for _ in range(3):
        _telegram_breaker.record_failure()
    summaries = [Summary(id="s1", article_id="a1", summary_text="S", model_used="test")]
    with pytest.raises(MessengerError, match="circuit breaker is open"):
        import asyncio

        asyncio.run(messenger.execute(summaries))


def test_records_failure_then_opens(messenger, monkeypatch):
    from unittest.mock import AsyncMock, patch

    monkeypatch.setattr(settings, "telegram_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "token")
    monkeypatch.setattr(settings, "telegram_chat_id", "chat")
    summaries = [Summary(id="s1", article_id="a1", summary_text="S", model_used="test")]
    with patch.object(messenger, "send_messages", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = False
        import asyncio

        assert asyncio.run(messenger.execute(summaries)) is False
    assert _telegram_breaker._failure_count == 1
    for _ in range(2):
        with patch.object(messenger, "send_messages", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = False
            assert asyncio.run(messenger.execute(summaries)) is False
    assert _telegram_breaker.state.value == "open"


def test_success_records_success(messenger, monkeypatch):
    from unittest.mock import AsyncMock, patch

    monkeypatch.setattr(settings, "telegram_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "token")
    monkeypatch.setattr(settings, "telegram_chat_id", "chat")
    _telegram_breaker.record_failure()
    _telegram_breaker.record_failure()
    summaries = [Summary(id="s1", article_id="a1", summary_text="S", model_used="test")]
    with patch.object(messenger, "send_messages", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        import asyncio

        assert asyncio.run(messenger.execute(summaries)) is True
    assert _telegram_breaker.state.value == "closed"
    assert _telegram_breaker._failure_count == 0


def test_missing_credentials_does_not_touch_breaker(messenger, monkeypatch):
    monkeypatch.setattr(settings, "telegram_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", None)
    monkeypatch.setattr(settings, "telegram_chat_id", None)
    summaries = [Summary(id="s1", article_id="a1", summary_text="S", model_used="test")]
    with pytest.raises(ConfigError):
        import asyncio

        asyncio.run(messenger.execute(summaries))
    assert _telegram_breaker._failure_count == 0