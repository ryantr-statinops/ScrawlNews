import logging

from src.services.bot import run_bot
from src.utils.logging import setup_logging


def main():
    setup_logging("INFO")
    logging.getLogger("bot").info("Starting Telegram bot")
    run_bot()


if __name__ == "__main__":
    main()