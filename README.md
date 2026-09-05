# budget-tracker

Documentation note:
- this README was written purely by Claude based on the checked-in repository contents at the time of update

Personal budget tracker with a backend-first monorepo layout.

Current focus:
- user-owned transactions and categories
- shared workspaces and relation-based collaboration
- async transaction writes through RabbitMQ + worker
- PostgreSQL as source of truth

Current repo status:
- monorepo shape is in place
- only the server runtime is implemented today
- docs and ops scaffolding already exist for local dev and future deployment

## Project description

`budget-tracker` is a personal finance system with an optional collaboration layer.

Core product model:
- each transaction belongs to one user
- categories are user-scoped
- workspaces group people, not base transaction ownership
- relations define shared views over transactions from workspace members
- analytics run on top of those relation-scoped views

Implementation direction in this repo today:
- synchronous reads through FastAPI
- asynchronous transaction writes through Celery + RabbitMQ
- PostgreSQL-backed persistence and Alembic migrations
- local Docker Compose stack for infra and app processes
- deployment scaffolding in `ops/`

## Monorepo layout

This repository is a small monorepo today: one implemented product runtime, plus shared docs and ops.

```text
budget-tracker/
├── README.md                  # repo-level overview, layout, architecture, onboarding
├── Makefile                   # root dev commands for server and local stack
├── docker-compose.yml         # local multi-service stack: postgres, rabbitmq, api, worker, nginx
├── server/                    # Python server project
│   ├── README.md              # server-local summary
│   ├── pyproject.toml         # server package metadata and tooling config
│   ├── alembic.ini            # migration config
│   ├── alembic/               # database migration environment + versions
│   ├── app/                   # application source
│   │   ├── api/               # FastAPI router, route modules, request deps
│   │   ├── core/              # config, db, logging, security primitives
│   │   ├── domain/            # enums, constants, permission rules
│   │   ├── health/            # health payload builders/checks
│   │   ├── models/            # SQLModel persistence models
│   │   ├── repos/             # database access layer
│   │   ├── schemas/           # request/response/command schemas
│   │   ├── services/          # app services, auth, command publishing, business logic
│   │   └── worker/            # Celery app, consumers, async tasks
│   └── tests/                 # unit + integration coverage
├── docker/                    # container build definitions
├── docs/                      # supporting docs for setup and workflows
├── idea/                      # product/design specs and longer-form planning docs
└── ops/                       # runtime and deployment scaffolding
    ├── k8s/                   # Kubernetes manifests
    └── nginx/                 # nginx reverse-proxy config
```

## Project map

### `server/`
Python server service.

Main responsibilities:
- expose HTTP APIs through FastAPI
- validate and enqueue transaction write commands
- read data from PostgreSQL for synchronous queries
- run worker-side command application through Celery

Key files:
- `server/app/main.py`
- `server/app/api/router.py`
- `server/app/services/transactions.py`
- `server/app/services/command_publisher.py`
- `server/app/worker/tasks/transactions.py`
- `server/app/core/config.py`
- `server/app/core/db.py`

### `docs/`
Support docs for contributors.

Current content:
- `docs/server-setup.md` — server local setup and command reference

### `idea/`
Product and architecture intent.

Current content:
- `idea/project_spec.md` — longer-form product, domain, API, and architecture spec

Use this as the detailed design source when repo code is still catching up to product intent.

### `ops/`
Operational scaffolding.

Current content:
- `ops/nginx/nginx.conf` — reverse proxy for local stack
- `ops/k8s/` — early Kubernetes manifests for api, worker, postgres, rabbitmq, ingress, config, secrets example

### Root infra files
- `docker-compose.yml` — local all-in-one stack
- `Makefile` — root shortcuts for install, run, test, lint, typecheck, migrations, Docker startup
- `docker/server.Dockerfile` — server container image definition

## Current architecture

## Runtime components

```text
client
  -> nginx
  -> FastAPI API
     -> PostgreSQL           # synchronous reads, durable state
     -> RabbitMQ             # async write queue
        -> Celery worker
           -> PostgreSQL     # applies create/update/delete commands
```

## Layering inside `server/app`

```text
api routes
  -> deps / auth context
  -> services
  -> repos
  -> models / db
```

Supporting paths:
- `schemas/` define request, response, and command payloads
- `domain/` holds shared enums/constants/permission primitives
- `worker/` consumes queued commands and applies idempotent writes

## What is implemented vs scaffolded

Implemented or partially implemented now:
- FastAPI app bootstrap and route registration
- transaction read endpoints and queued write flow
- Celery app + RabbitMQ-backed command publishing
- worker task handlers for create, update, delete transaction commands
- SQLModel models, DB config, and Alembic foundation
- unit and integration test directories
- docker-compose local runtime

Scaffold or placeholder today:
- auth still uses a dev current-user adapter
- categories/workspaces/relations/analytics endpoints are mostly placeholders
- Kubernetes manifests are starter scaffolding, not hardened production infra

## API and data-flow notes

### Read path
- request enters FastAPI
- route resolves current user and DB session
- repo/service reads PostgreSQL directly
- response returns synchronously

### Write path for transactions
- request enters FastAPI
- service generates `message_id`, `operation_key`, and `transaction_id` when needed
- command publisher sends payload to RabbitMQ via Celery
- API returns `202 queued`
- worker consumes command and applies newest valid operation to PostgreSQL

Representative files:
- `server/app/api/routes/transactions.py`
- `server/app/services/transactions.py`
- `server/app/services/command_publisher.py`
- `server/app/worker/tasks/transactions.py`
- `server/app/worker/consumers/transaction_commands.py`

## Local development quick start

## Server-only local flow

- Copy `.env.example` to `.env`
- Use Python `3.11+`
- Run `make install`
- If your editor still misses imports, select `.venv/bin/python`
- Start infra: `docker compose up -d postgres rabbitmq`
- Run migrations: `make migrate-up`
- Start API: `make run-api`
- Start worker: `make run-worker`

## Full local stack

- Run `docker compose up --build`
- API: `http://localhost:8000`
- nginx: `http://localhost`
- RabbitMQ management: `http://localhost:15672`

## Common commands

- `make test`
- `make lint`
- `make typecheck`
- `make docker-up`

## README structure guide

This root README should stay repo-oriented, not server-only.

Recommended section order:
1. project summary
2. monorepo layout
3. project map by top-level directory
4. current architecture and runtime flow
5. local development quick start
6. status: implemented vs scaffolded
7. contributor guide for keeping docs updated

Rules:
- keep root README focused on repo navigation and system shape
- keep component-specific runbooks in local READMEs or `docs/`
- link to detailed specs instead of duplicating long design text here
- prefer current-state descriptions over aspirational wording
- when a section becomes long, move details into `docs/` and leave a short summary + link here

Good split of responsibility:
- `README.md` — repo summary only
- `server/README.md` — server package-specific details
- `docs/*.md` — setup guides, runbooks, contributor docs
- `idea/*.md` — product/design intent and future architecture notes
- `ops/` — runnable infra config, not prose documentation

## How to update this README iteratively

Update this file whenever one of these changes:
- a new top-level project or directory is added
- a new runtime component is introduced
- ownership of a directory changes
- a placeholder area becomes implemented
- local dev commands or bootstrap flow changes

Preferred update workflow:
1. update the layout tree if top-level or major subdirectories changed
2. update the project map with one-line responsibility changes
3. update the architecture section if request/data flow changed
4. update quick-start commands if startup flow changed
5. update implemented vs scaffolded notes so status stays honest
6. add links to new detailed docs instead of bloating this file

Editing rules:
- describe current truth from code and checked-in config
- mark future work explicitly as future work
- avoid copying large blocks from `idea/project_spec.md`
- keep top-level directory descriptions to one or two lines each
- keep file references concrete and clickable when possible

## Suggested triggers for future README updates

Examples:
- frontend or mobile app added
  - add it to the layout tree
  - add a project-map section for it
  - update architecture with how it talks to server
- shared package/library added
  - document why it exists and which projects consume it
- auth stops being placeholder-only
  - replace the scaffold note with real auth flow summary
- analytics becomes implemented
  - replace placeholder note with actual query/data-flow summary
- production deploy path becomes real
  - promote `ops/` from scaffold note to deployment overview

## Source-of-truth pointers

Use these files when refreshing this README:
- `README.md` — repo summary only
- `docs/server-setup.md` — current local server setup
- `idea/project_spec.md` — product/domain intent
- `server/app/main.py` — app entrypoint
- `server/app/api/router.py` — mounted route surface
- `server/app/core/config.py` — runtime config surface
- `server/app/worker/celery_app.py` — async runtime setup
- `docker-compose.yml` — local service topology
- `ops/k8s/` — deployment scaffold inventory

## Current summary

Today this monorepo is best understood as:
- one real server project in `server/`
- shared repo-level docs in `docs/` and `idea/`
- shared deployment scaffolding in `ops/`
- root-level tooling that ties the whole stack together

As more apps or shared packages are added, keep this README as the short map of the whole repo, and push component detail downward into the component that owns it.
