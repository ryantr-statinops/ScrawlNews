from fastapi import FastAPI
from src.api.routes import articles, runs, config, health, summaries

app = FastAPI(title="ScrawlNews Dashboard", version="0.2.0")

app.include_router(articles.router)
app.include_router(runs.router)
app.include_router(config.router)
app.include_router(health.router)
app.include_router(summaries.router)
