import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import settings
from src.repositories.article_repo import ArticleRepository
from src.repositories.config_repo import ConfigRepository
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


async def cmd_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("Usage: /topic <category>")
        return
    category = context.args[0].strip().lower()
    article_repo = ArticleRepository(settings.database_url)
    articles = article_repo.get_recent_by_category(category, limit=10)
    if not articles:
        await update.effective_message.reply_text(f"No articles for category '{category}'.")
        return
    lines = [f"*Latest {category} news:*"]
    for a in articles:
        title = a["title"][:80]
        lines.append(f"- {title} — /detail {a['id']}")
    await update.effective_message.reply_text(
        "\n".join(lines), disable_web_page_preview=True
    )


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config_repo = ConfigRepository(settings.database_url)
    overrides = config_repo.get_all()
    categories = overrides.get("news_categories", settings.news_categories)
    frequency = overrides.get("schedule_interval_hours", str(settings.schedule_interval_hours))
    telegram_enabled = overrides.get("telegram_enabled", str(settings.telegram_enabled))
    text = (
        "Current settings:\n"
        f"- Categories: {categories}\n"
        f"- Frequency: every {frequency}h\n"
        f"- Telegram: {'on' if telegram_enabled.lower() == 'true' else 'off'}\n\n"
        "Change with:\n"
        "/settings categories <a,b,c>\n"
        "/settings frequency <hours>"
    )
    await update.effective_message.reply_text(text)


def build_bot_app(token: str | None = None) -> Application:
    bot_token = token or settings.telegram_bot_token
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("detail", cmd_detail))
    app.add_handler(CommandHandler("topic", cmd_topic))
    app.add_handler(CommandHandler("settings", cmd_settings))
    return app


def run_bot() -> None:
    app = build_bot_app()
    app.run_polling()
