import logging

from telegram.error import TelegramError

from src.config import settings
from src.services.bot import run_bot
from src.utils.logging import setup_logging


def main():
    setup_logging("INFO")
    logger = logging.getLogger("bot")
    if not settings.telegram_enabled:
        logger.info("Telegram bot disabled; exiting cleanly")
        return
    logger.info("Starting Telegram bot")
    try:
        run_bot()
    except (TelegramError, ValueError) as exc:
        logger.error("Telegram bot unavailable; dashboard remains usable: %s", exc)


if __name__ == "__main__":
    main()
