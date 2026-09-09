import asyncio
from typing import cast

from telegram import Bot
from telegram.error import BadRequest, NetworkError, RetryAfter, TelegramError

from src.config import settings
from src.models.summary import Summary
from src.services.base import BaseService
from src.utils.circuit_breaker import CircuitBreaker
from src.utils.errors import ConfigError, MessengerError

_telegram_breaker = CircuitBreaker("telegram", failure_threshold=3, cooldown_seconds=120)


class MessengerService(BaseService):
    async def execute(self, summaries: list[Summary]) -> bool:
        if not settings.telegram_enabled:
            return True
        if not summaries:
            return True
        if not _telegram_breaker.allow_request():
            raise MessengerError("Telegram circuit breaker is open", retryable=False)
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            raise ConfigError("Telegram is enabled but credentials are missing")
        text = self.format_message(summaries)
        parts = self.split_message(text)
        try:
            result = await self.send_messages(settings.telegram_chat_id, parts)
            if result:
                _telegram_breaker.record_success()
            else:
                _telegram_breaker.record_failure()
            return result
        except MessengerError:
            _telegram_breaker.record_failure()
            raise

    def format_message(self, summaries: list[Summary]) -> str:
        lines = ["Daily News Briefing\n"]
        for s in summaries:
            lines.append(f"- {s.summary_text}")
        return "\n".join(lines)

    def split_message(self, text: str, max_len: int = 4000) -> list[str]:
        if len(text) <= max_len:
            return [text]
        parts = text.split("\n\n")
        messages: list[str] = []
        current = ""
        for part in parts:
            if len(current) + len(part) + 2 <= max_len:
                current += part + "\n\n"
            else:
                messages.append(current.strip())
                current = part + "\n\n"
        if current:
            messages.append(current.strip())
        return messages

    async def send_messages(self, chat_id: str, messages: list[str]) -> bool:
        # execute() validates credentials before invoking this transport helper.
        token = cast(str, settings.telegram_bot_token)
        try:
            bot = Bot(token=token)
            for msg in messages:
                try:
                    await bot.send_message(chat_id=chat_id, text=msg)
                except RetryAfter as e:
                    retry_after = getattr(e, "retry_after", 0)
                    if hasattr(retry_after, "total_seconds"):
                        retry_after = retry_after.total_seconds()
                    await asyncio.sleep(float(retry_after))
                    await bot.send_message(chat_id=chat_id, text=msg)
                await asyncio.sleep(1)
            return True
        except TelegramError as exc:
            # BadRequest inherits NetworkError but is not a transient failure.
            raise MessengerError(
                "Telegram request failed",
                retryable=isinstance(exc, (NetworkError, RetryAfter))
                and not isinstance(exc, BadRequest),
            ) from exc
