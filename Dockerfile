FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

WORKDIR /app

COPY --from=uv /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    alembic \
    asyncpg \
    redis \
    pydantic \
    pydantic-settings \
    "python-jose[cryptography]" \
    "passlib[bcrypt]" \
    python-multipart \
    cryptography \
    ecdsa \
    pyasn1 \
    idna \
    python-dotenv \
    Mako \
    starlette \
    email-validator \
    python-dateutil \
    httpx

COPY --chown=appuser:appuser . .
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

EXPOSE 8000

USER appuser

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
