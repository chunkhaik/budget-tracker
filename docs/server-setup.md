# Server setup

## Local development

### Requirements

- Run from repo root: `/Users/bytedance/Dev/-personal/budget-tracker`
- Use Python `3.11+`
- Docker is required for local Postgres and RabbitMQ

### First-time setup

Run these once before starting the app:

1. Copy env file
   - `cp .env.example .env`
2. Create the local venv and install server deps
   - `make install`
3. If Pylance still shows missing imports, select the repo interpreter at `.venv/bin/python`

### Local run order

Use this exact order for local dev:

1. Start infra
   - `docker compose up -d postgres rabbitmq`
2. Apply database schema
   - `make migrate-up`
3. Start the API
   - `make run-api`
4. Start the worker
   - `make run-worker`

If you skip `make migrate-up`, read endpoints fail with DB errors like `relation "transactions" does not exist`.
If you change Celery task registration code, restart the worker so it reloads task imports.

### Recommended tab split

- `Tab 1` — infra
  - `docker compose up -d postgres rabbitmq`
- `Tab 2` — API
  - `make run-api`
- `Tab 3` — worker
  - `make run-worker`
- `Tab 4` — manual API testing
  - `curl ...`

### Local URLs and route prefixes

- API base: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Transaction routes are under `/v1`, not `/api/v1`
  - example: `http://localhost:8000/v1/transactions`

### Smoke tests

Once API + DB are up and migrations are applied:

- Health check
  - `curl http://localhost:8000/health`
- List transactions
  - `curl http://localhost:8000/v1/transactions`

For transaction create/update/delete flows, keep the worker running too.

## Local commands without shell activation

- Verify imports: `./.venv/bin/python -c "import fastapi, sqlmodel, celery, psycopg"`
- Run tests: `make test`
- Run type checks: `make typecheck`
- Run compile checks: `make lint`
- Re-apply latest migrations: `make migrate-up`

## Optional shell activation

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `cd server && python -m pip install -e '.[dev]'`

## Docker stack

- Run `docker compose up --build`
- API: `http://localhost:8000`
- Nginx: `http://localhost`
- RabbitMQ management: `http://localhost:15672`

Note:
- `http://localhost` only works when the nginx service is running in the full Docker stack
- when running API locally with `make run-api`, use `http://localhost:8000`

## Current scaffold notes

- Auth is still placeholder-only; FastAPI uses a dev current user dependency.
- Transaction writes now persist through Celery/RabbitMQ worker handlers.
- Transaction reads now load from the database for the current user.
- SQLModel models and Alembic migration cover the first-pass schema foundation.
- Kubernetes manifests in `ops/k8s/` are scaffold-level only and should be hardened before real deployment.
