import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import settings

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "ScrawlNews Bot\n\n"
    "/start — show intro\n"
    "/detail <id> — full summary + original link\n"
    "/topic <category> — latest articles in a category\n"
    "/settings — show current settings\n"
    "/settings categories <a,b,c> — set news categories\n"
    "/settings frequency <hours> — set briefing interval"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Xin chào! Mình là ScrawlNews Bot 📰\n\n" + HELP_TEXT
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP_TEXT)


def build_bot_app(token: str | None = None) -> Application:
    bot_token = token or settings.telegram_bot_token
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    return app


def run_bot() -> None:
    app = build_bot_app()
    app.run_polling()