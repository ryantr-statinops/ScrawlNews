import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import settings
from src.repositories.article_repo import ArticleRepository
from src.repositories.summary_repo import SummaryRepository

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


async def cmd_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("Usage: /detail <article_id>")
        return
    article_id = context.args[0]
    article_repo = ArticleRepository(settings.database_url)
    summary_repo = SummaryRepository(settings.database_url)
    article = article_repo.get_by_id(article_id)
    summaries = summary_repo.get_by_article(article_id)
    if article is None:
        await update.effective_message.reply_text(f"Article {article_id} not found.")
        return
    summary_text = summaries[0]["summary_text"] if summaries else article["title"]
    category = article.get("category") or "uncategorized"
    lines = [
        f"*{article['title']}*",
        f"\n{summary_text}",
        f"\nCategory: {category}\nSource: {article['source']}",
        f"Link: {article['url']}",
    ]
    await update.effective_message.reply_text("\n".join(lines), disable_web_page_preview=True)


def build_bot_app(token: str | None = None) -> Application:
    bot_token = token or settings.telegram_bot_token
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("detail", cmd_detail))
    return app


def run_bot() -> None:
    app = build_bot_app()
    app.run_polling()
