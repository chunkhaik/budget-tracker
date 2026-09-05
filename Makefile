PYTHON ?= python3.11
SERVER_DIR := server
VENV_DIR := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_PYTHON) -m pip
VENV_UVICORN := $(VENV_DIR)/bin/uvicorn
VENV_CELERY := $(VENV_DIR)/bin/celery
VENV_ALEMBIC := $(VENV_DIR)/bin/alembic
VENV_MYPY := $(VENV_DIR)/bin/mypy
VENV_PYTEST := $(VENV_DIR)/bin/pytest

.PHONY: venv install run-api run-worker test lint typecheck migrate-up docker-up

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install --upgrade pip
	cd $(SERVER_DIR) && ../$(VENV_PYTHON) -m pip install -e .[dev]

install: venv

run-api:
	cd $(SERVER_DIR) && ../$(VENV_UVICORN) app.main:app --reload

run-worker:
	cd $(SERVER_DIR) && ../$(VENV_CELERY) -A app.worker.celery_app.celery_app worker --loglevel=info

test:
	cd $(SERVER_DIR) && ../$(VENV_PYTEST)

lint:
	cd $(SERVER_DIR) && ../$(VENV_PYTHON) -m compileall app tests

typecheck:
	cd $(SERVER_DIR) && ../$(VENV_MYPY) app tests

migrate-up:
	cd $(SERVER_DIR) && ../$(VENV_ALEMBIC) upgrade head

docker-up:
	docker compose up --build
