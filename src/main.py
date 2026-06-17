from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.goals import router as goals_router
from src.api.v1.users import router as users_router
from src.api.v1.workouts import router as workouts_router
from src.core.cache import cache_service
from src.core.config import settings
from src.core.exceptions import AppError
from src.core.logging import get_logger, setup_logging
from src.core.middleware import RequestIDMiddleware, TimingMiddleware

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Запуск приложения TrackFit Pro API")
    await cache_service.connect()
    yield
    logger.info("Остановка приложения TrackFit Pro API")
    await cache_service.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Профессиональный REST API для отслеживания фитнес-активности",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "users",
            "description": "Регистрация, аутентификация и управление профилем",
        },
        {
            "name": "workouts",
            "description": "CRUD тренировок, статистика и аналитика",
        },
        {
            "name": "goals",
            "description": "Постановка и отслеживание фитнес-целей",
        },
        {"name": "health", "description": "Проверка состояния сервиса"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)

app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(workouts_router, prefix=settings.API_V1_PREFIX)
app.include_router(goals_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("AppError: %d — %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning("Validation error: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, Any]:
    checks: dict[str, str] = {}

    if cache_service.available and cache_service.redis is not None:
        try:
            _ = await cache_service.redis.ping()  # type: ignore[misc]
            checks["redis"] = "connected"
        except Exception:
            checks["redis"] = "unavailable"
    else:
        checks["redis"] = "disabled"

    return {"status": "healthy", "checks": checks}
