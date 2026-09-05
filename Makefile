PYTHON ?= python3
BACKEND_DIR := backend

.PHONY: install run-api run-worker test lint migrate-up docker-up

install:
	cd $(BACKEND_DIR) && $(PYTHON) -m pip install -e .[dev]

run-api:
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload

run-worker:
	cd $(BACKEND_DIR) && celery -A app.worker.celery_app.celery_app worker --loglevel=info

test:
	cd $(BACKEND_DIR) && pytest

lint:
	cd $(BACKEND_DIR) && python -m compileall app tests

migrate-up:
	cd $(BACKEND_DIR) && alembic upgrade head

docker-up:
	docker compose up --build
