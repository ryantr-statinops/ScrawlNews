from unittest.mock import AsyncMock, MagicMock

import pytest

from src.config import settings
from src.services.bot import (
    _parse_settings_args,
    build_bot_app,
    cmd_detail,
    cmd_help,
    cmd_settings,
    cmd_start,
    cmd_topic,
)


def make_update() -> tuple[MagicMock, MagicMock, AsyncMock]:
    msg = AsyncMock()
    update = MagicMock()
    update.effective_message = msg
    context = MagicMock()
    context.args = []
    return update, context, msg


@pytest.mark.asyncio
async def test_cmd_start_replies():
    update, context, msg = make_update()
    await cmd_start(update, context)
    assert msg.reply_text.await_count == 1


@pytest.mark.asyncio
async def test_cmd_help_replies():
    update, context, msg = make_update()
    await cmd_help(update, context)
    text = msg.reply_text.await_args.args[0]
    assert "/detail" in text and "/topic" in text and "/settings" in text


@pytest.mark.asyncio
async def test_detail_no_args():
    update, context, msg = make_update()
    await cmd_detail(update, context)
    assert "Usage" in msg.reply_text.await_args.args[0]


@pytest.mark.asyncio
async def test_detail_not_found():
    update, context, msg = make_update()
    context.args = ["nonexistent"]
    await cmd_detail(update, context)
    assert "not found" in msg.reply_text.await_args.args[0]


@pytest.mark.asyncio
async def test_topic_no_args():
    update, context, msg = make_update()
    await cmd_topic(update, context)
    assert "Usage" in msg.reply_text.await_args.args[0]


@pytest.mark.asyncio
async def test_topic_no_results():
    update, context, msg = make_update()
    context.args = ["sports"]
    await cmd_topic(update, context)
    text = msg.reply_text.await_args.args[0]
    assert "No articles" in text


@pytest.mark.asyncio
async def test_settings_view(monkeypatch):
    from src.repositories.config_repo import ConfigRepository

    repo = ConfigRepository(settings.database_url)
    repo.set("news_categories", "tech,ai")
    repo.set("schedule_interval_hours", "12")
    update, context, msg = make_update()
    await cmd_settings(update, context)
    text = msg.reply_text.await_args.args[0]
    assert "tech,ai" in text
    assert "12" in text


@pytest.mark.asyncio
async def test_settings_update_categories(monkeypatch):
    from src.repositories.config_repo import ConfigRepository

    update, context, msg = make_update()
    context.args = ["categories", "tech,business"]
    await cmd_settings(update, context)
    text = msg.reply_text.await_args.args[0]
    assert "Updated news_categories = tech,business" in text
    assert ConfigRepository(settings.database_url).get("news_categories") == "tech,business"


def test_parse_settings_args_categories():
    assert _parse_settings_args(["categories", "tech,ai"]) == ("news_categories", "tech,ai")


def test_parse_settings_args_frequency():
    assert _parse_settings_args(["frequency", "12"]) == ("schedule_interval_hours", "12")


def test_parse_settings_args_invalid_frequency():
    assert _parse_settings_args(["frequency", "abc"]) == (None, None)
    assert _parse_settings_args(["frequency", "0"]) == (None, None)


def test_parse_settings_args_unknown():
    assert _parse_settings_args(["bogus", "x"]) == (None, None)


def test_build_bot_app_registers_handlers():
    app = build_bot_app("dummy")
    names = {h.callback.__name__ for h in app.handlers[0]}
    assert names == {"cmd_start", "cmd_help", "cmd_detail", "cmd_topic", "cmd_settings"}
