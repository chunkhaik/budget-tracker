FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY server/README.md ./README.md
COPY server/pyproject.toml ./pyproject.toml
COPY server/app ./app
COPY server/alembic ./alembic
COPY server/alembic.ini ./alembic.ini

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
