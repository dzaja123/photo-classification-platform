# ---------- builder ----------
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/application/requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- production ----------
FROM python:3.11-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /install /usr/local

WORKDIR /workspace
COPY shared/ /workspace/shared/
COPY services/application/ /workspace/services/application/

ENV PYTHONPATH=/workspace \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace/services/application

USER app
EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
