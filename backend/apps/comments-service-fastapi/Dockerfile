FROM python:3.12-slim AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1

COPY backend/apps/comments-service-fastapi/requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime

WORKDIR /app/service

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/libs:/app/libs/events:/app/libs/context-service

COPY --from=builder /install /usr/local
COPY libs /app/libs
COPY backend/apps/comments-service-fastapi /app/service

EXPOSE 8004

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "4"]
