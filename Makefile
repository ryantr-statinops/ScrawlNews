.PHONY: install dev worker beat run test lint format typecheck clean

install:
	pip install --break-system-packages -r requirements.txt
	playwright install chromium || true
	cd web && npm install

dev:
	docker-compose down 2>/dev/null || true
	lsof -i :8000 -sTCP:LISTEN -t 2>/dev/null | xargs -r kill -9 || true
	lsof -i :5173 -sTCP:LISTEN -t 2>/dev/null | xargs -r kill -9 || true
	docker-compose up -d redis
	docker-compose up -d --no-deps nginx
	npx concurrently "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload" "celery -A src.worker.celery_app worker --loglevel=info" "celery -A src.worker.celery_app beat --loglevel=info" "cd web && npm run dev"

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
	cd web && npm run lint

format:
	ruff format src/

typecheck:
	mypy src/
	cd web && npm run typecheck

clean:
	rm -rf .pytest_cache .ruff_cache web/node_modules web/dist data/scrawlnews.db logs/*.log
