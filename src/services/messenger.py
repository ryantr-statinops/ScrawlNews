import asyncio

from src.config import settings
from src.models.summary import Summary
from src.services.base import BaseService


class MessengerService(BaseService):
    async def execute(self, summaries: list[Summary]) -> bool:
        if not settings.telegram_enabled:
            return True
        if not summaries:
            return True
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return False
        text = self.format_message(summaries)
        parts = self.split_message(text)
        return await self.send_messages(settings.telegram_chat_id, parts)

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
        # Stage 2 stub: avoid real Telegram call in tests, just simulate
        try:
            from telegram import Bot

            bot = Bot(token=settings.telegram_bot_token)
            for msg in messages:
                await bot.send_message(chat_id=chat_id, text=msg)
                await asyncio.sleep(1)
            return True
        except Exception:
            return False
