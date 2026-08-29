from unittest.mock import AsyncMock, patch

import pytest

from src.models.summary import Summary
from src.services.messenger import MessengerService


@pytest.mark.asyncio
async def test_send_message_success(mock_telegram_bot):
    service = MessengerService()
    summaries = [
        Summary(id="s1", article_id="a1", summary_text="Summary 1", model_used="gpt-4o-mini"),
        Summary(id="s2", article_id="a2", summary_text="Summary 2", model_used="gpt-4o-mini"),
    ]
    with patch("src.config.settings.telegram_bot_token", "token"):
        with patch("src.config.settings.telegram_chat_id", "123"):
            with patch.object(service, "send_messages", return_value=True) as mock_send:
                result = await service.execute(summaries)
                assert result is True
                mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_disabled():
    service = MessengerService()
    with patch.object(service, "send_messages") as mock_send:
        result = await service.execute([])
        assert result is True
        mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_missing_credentials():
    service = MessengerService()
    summaries = [Summary(id="s1", article_id="a1", summary_text="T", model_used="m")]
    with patch("src.config.settings.telegram_bot_token", None):
        with patch("src.config.settings.telegram_chat_id", None):
            result = await service.execute(summaries)
            assert result is False


def test_format_message():
    service = MessengerService()
    summaries = [
        Summary(id="s1", article_id="a1", summary_text="Summary 1", model_used="m"),
        Summary(id="s2", article_id="a2", summary_text="Summary 2", model_used="m"),
    ]
    text = service.format_message(summaries)
    assert "Daily News Briefing" in text
    assert "Summary 1" in text
    assert "Summary 2" in text


def test_split_message_short():
    service = MessengerService()
    text = "Short message"
    parts = service.split_message(text, max_len=4000)
    assert len(parts) == 1
    assert parts[0] == text


def test_split_message_long():
    service = MessengerService()
    text = "Paragraph 1\n\n" + "Paragraph 2\n\n" + "Paragraph 3"
    parts = service.split_message(text, max_len=20)
    assert len(parts) > 1
    for part in parts:
        assert len(part) <= 20


@pytest.mark.asyncio
async def test_send_messages_rate_limit(mock_telegram_bot):
    from unittest.mock import MagicMock

    from telegram.error import RetryAfter

    service = MessengerService()
    mock_telegram_bot.send_message.side_effect = [
        RetryAfter(retry_after=0),
        MagicMock(),
        MagicMock(),
    ]
    with patch("asyncio.sleep"):
        with patch("src.config.settings.telegram_bot_token", "token"):
            with patch("src.config.settings.telegram_chat_id", "123"):
                result = await service.send_messages("123", ["msg1", "msg2"])
                assert result is True
