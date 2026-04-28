FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    DATABASE_PATH=/app/data/app.db \
    SKIP_INSTALL=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY pyproject.toml README.md run.sh ./
COPY src ./src

RUN mkdir -p /app/data \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && chmod +x /app/run.sh \
    && chown -R appuser:appuser /app/data

USER appuser

EXPOSE 8000

CMD ["./run.sh"]
