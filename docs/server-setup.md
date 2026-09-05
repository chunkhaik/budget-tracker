# Server setup

## Local development

- Copy `.env.example` to `.env`
- Create the local venv and install server deps: `make install`
- This repo currently runs on Python `3.11+`
- If Pylance still shows missing imports, select the repo interpreter at `.venv/bin/python`
- Start infra only: `docker compose up -d postgres rabbitmq`
- Run migrations locally: `make migrate-up`
- Run the API locally: `make run-api`
- Run the worker locally: `make run-worker`

## Local commands without shell activation

- Verify imports: `./.venv/bin/python -c "import fastapi, sqlmodel, celery, psycopg"`
- Run tests: `make test`
- Run type checks: `make typecheck`
- Run compile checks: `make lint`

## Optional shell activation

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `cd server && python -m pip install -e '.[dev]'`

## Docker stack

- Run `docker compose up --build`
- API: `http://localhost:8000`
- Nginx: `http://localhost`
- RabbitMQ management: `http://localhost:15672`

## Current scaffold notes

- Auth is still placeholder-only; FastAPI uses a dev current user dependency.
- Transaction writes now persist through Celery/RabbitMQ worker handlers.
- Transaction reads now load from the database for the current user.
- SQLModel models and Alembic migration cover the first-pass schema foundation.
- Kubernetes manifests in `ops/k8s/` are scaffold-level only and should be hardened before real deployment.
