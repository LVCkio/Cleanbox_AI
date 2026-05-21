# ─────────────────────────────────────────────────────
# CleanInbox AI — Dockerfile (Backend FastAPI)
# Multi-stage build để giữ image nhỏ gọn
# ─────────────────────────────────────────────────────

# Stage 1: Builder — cài dependencies
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime — image sạch, chỉ copy những gì cần
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages từ builder
COPY --from=builder /install /usr/local

# Copy source code
COPY backend/ ./backend/
COPY fatigue_intelligence/ ./fatigue_intelligence/
COPY .env.example ./.env

# Tạo user non-root (bảo mật)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# Chạy với uvicorn (production: dùng gunicorn + uvicorn workers)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
