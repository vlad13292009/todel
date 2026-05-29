FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install --user -r requirements.txt -r requirements-dev.txt

FROM python:3.11-slim AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

RUN python manage.py collectstatic --noinput

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "quiz_service.wsgi:application"]
