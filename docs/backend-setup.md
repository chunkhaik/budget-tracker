# Backend setup

## Local development

- Copy `.env.example` to `.env`
- Run `make install`
- Run `docker compose up -d postgres rabbitmq`
- Run `make migrate-up`
- Run `make run-api`
- Run `make run-worker`

## Docker stack

- Run `docker compose up --build`
- API: `http://localhost:8000`
- Nginx: `http://localhost`
- RabbitMQ management: `http://localhost:15672`

## Current scaffold notes

- Auth is still placeholder-only; FastAPI uses a dev current user dependency.
- Transaction writes are queued through Celery/RabbitMQ entrypoints, but worker DB mutation logic is still stubbed.
- SQLModel models and Alembic migration cover the first-pass schema foundation.
- Kubernetes manifests in `ops/k8s/` are scaffold-level only and should be hardened before real deployment.
