import asyncio
from collections import defaultdict

import dagster as dg

from src.config import settings
from src.dagster_project.shadow import isolated_settings
from src.models.article import Article
from src.models.digest import Digest
from src.models.summary import Summary
from src.services.digest_service import DigestService
from src.services.scrawler import ScrawlerService
from src.worker.tasks import _synthesize_articles


@dg.asset(group_name="shadow")
def rss_ingestion(context: dg.AssetExecutionContext) -> list[Article]:
    with isolated_settings(context.run_id):
        articles = asyncio.run(
            ScrawlerService().execute(
                limit=settings.dagster_shadow_limit,
                categories=settings.dagster_shadow_categories_list,
            )
        )
    context.add_output_metadata({"article_count": len(articles), "domain_db_mutated": False})
    return articles


@dg.asset(group_name="shadow")
def article_extraction(context: dg.AssetExecutionContext, rss_ingestion: list[Article]) -> list[Article]:
    extracted = sum(bool(article.content) for article in rss_ingestion)
    context.add_output_metadata({"article_count": len(rss_ingestion), "extracted_count": extracted})
    return rss_ingestion


@dg.asset(group_name="shadow")
def article_normalization(context: dg.AssetExecutionContext, article_extraction: list[Article]) -> list[Article]:
    normalized = [article for article in article_extraction if article.id and article.url and article.title]
    context.add_output_metadata({"article_count": len(normalized), "dropped_count": len(article_extraction) - len(normalized)})
    return normalized


@dg.asset(group_name="shadow")
def article_summarization(context: dg.AssetExecutionContext, article_normalization: list[Article]) -> list[Summary]:
    with isolated_settings(context.run_id):
        summaries = asyncio.run(_synthesize_articles(article_normalization, run_id=context.run_id))
    context.add_output_metadata({"summary_count": len(summaries), "telegram_sent": 0})
    return summaries


@dg.asset(group_name="shadow")
def topic_digest_generation(
    context: dg.AssetExecutionContext,
    article_normalization: list[Article],
    article_summarization: list[Summary],
) -> list[Digest]:
    by_category: dict[str, list[Article]] = defaultdict(list)
    for article in article_normalization:
        by_category[article.category or "uncategorized"].append(article)
    summaries_by_article = {summary.article_id: summary for summary in article_summarization}
    digests: list[Digest] = []
    with isolated_settings(context.run_id):
        for category, articles in by_category.items():
            service = DigestService()
            try:
                summaries = [summaries_by_article[article.id] for article in articles if article.id in summaries_by_article]
                digests.append(asyncio.run(service.execute(category, articles, summaries, run_id=context.run_id)))
            finally:
                asyncio.run(service.close())
    context.add_output_metadata({"digest_count": len(digests), "telegram_sent": 0})
    return digests


@dg.asset(group_name="shadow")
def delivery_simulation(context: dg.AssetExecutionContext, topic_digest_generation: list[Digest]) -> dict:
    result = {"digest_count": len(topic_digest_generation), "telegram_sent": 0, "simulated": True}
    context.add_output_metadata(result)
    return result


defs = dg.Definitions(assets=[
    rss_ingestion,
    article_extraction,
    article_normalization,
    article_summarization,
    topic_digest_generation,
    delivery_simulation,
])
