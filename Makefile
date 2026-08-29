.PHONY: install dev worker beat run test lint format typecheck clean

install:
	pip install -r requirements.txt
	playwright install chromium || true
	cd web && npm install

dev:
	docker compose up -d nginx redis
	concurrently "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload" "celery -A src.worker.celery_app worker --loglevel=info" "celery -A src.worker.celery_app beat --loglevel=info" "cd web && npm run dev"

worker:
	celery -A src.worker.celery_app worker --loglevel=info

beat:
	celery -A src.worker.celery_app beat --loglevel=info

run:
	python src/main.py --dry-run

test:
	pytest tests/ --cov=src --cov-report=term-missing
	cd web && npm run test

lint:
	ruff check src/
	cd web && npx eslint src --ext ts,tsx || true

format:
	ruff format src/

typecheck:
	mypy src/
	cd web && npm run typecheck

clean:
	rm -rf .pytest_cache .ruff_cache web/node_modules web/dist data/scrawlnews.db logs/*.log
