.PHONY: install dev worker beat run test lint format typecheck clean

install:
	pip install --break-system-packages -r requirements.txt
	playwright install chromium || true
	cd frontend && npm install

dev:
	docker-compose down 2>/dev/null || true
	lsof -i :8000 -sTCP:LISTEN -t 2>/dev/null | xargs -r kill -9 || true
	lsof -i :5173 -sTCP:LISTEN -t 2>/dev/null | xargs -r kill -9 || true
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d redis nginx
	npx concurrently "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload" "celery -A src.worker.celery_app worker --loglevel=info" "celery -A src.worker.celery_app beat --loglevel=info" "cd frontend && npm run dev"

worker:
	celery -A src.worker.celery_app worker --loglevel=info

beat:
	celery -A src.worker.celery_app beat --loglevel=info

run:
	python src/main.py --dry-run

test:
	pytest tests/ --cov=src --cov-report=term-missing
	cd frontend && npm run test

lint:
	ruff check src/
	cd frontend && npm run lint

format:
	ruff format src/

typecheck:
	mypy src/
	cd frontend && npm run typecheck

clean:
	rm -rf .pytest_cache .ruff_cache frontend/node_modules frontend/dist data/scrawlnews.db logs/*.log
