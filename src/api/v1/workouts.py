from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.core.cache import cache_service
from src.core.database import get_db
from src.core.logging import get_logger
from src.models.models import User, WorkoutType
from src.schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutStats, WorkoutUpdate
from src.services.workout_service import WorkoutService

logger = get_logger(__name__)
router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkoutResponse:
    logger.info("Создание тренировки для пользователя: ID %d", current_user.id)

    workout = await WorkoutService.create_workout(db, current_user.id, workout_data)
    await db.commit()

    await cache_service.delete_pattern(f"user:{current_user.id}:*")

    return WorkoutResponse.model_validate(workout)


@router.get("", response_model=list[WorkoutResponse])
async def get_workouts(
    skip: Annotated[int, Query(0, ge=0)] = 0,
    limit: Annotated[int, Query(100, ge=1, le=500)] = 100,
    workout_type: WorkoutType | None = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> list[WorkoutResponse]:
    cache_key = f"user:{current_user.id}:workouts:{skip}:{limit}:{workout_type}"

    cached = await cache_service.get_json(cache_key)
    if cached:
        logger.info("Получение тренировок из кэша для пользователя: ID %d", current_user.id)
        return [WorkoutResponse(**w) for w in cached]

    workouts = await WorkoutService.get_user_workouts(
        db, current_user.id, skip, limit, workout_type
    )

    result = [WorkoutResponse.model_validate(w) for w in workouts]

    await cache_service.set_json(
        cache_key,
        [r.model_dump(mode="json") for r in result],
        expire=timedelta(minutes=5),
    )

    return result


@router.get("/stats", response_model=WorkoutStats)
async def get_workout_stats(
    days: Annotated[int, Query(30, ge=1, le=365)] = 30,
    current_user: Annotated[User, Depends(get_current_user)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> WorkoutStats:
    cache_key = f"user:{current_user.id}:stats:{days}"

    cached = await cache_service.get_json(cache_key)
    if cached:
        logger.info("Получение статистики из кэша для пользователя: ID %d", current_user.id)
        return WorkoutStats(**cached)

    stats = await WorkoutService.get_workout_statistics(db, current_user.id, days)

    await cache_service.set_json(
        cache_key,
        stats.model_dump(),
        expire=timedelta(minutes=10),
    )

    return stats


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkoutResponse:
    workout = await WorkoutService.get_workout_by_id(db, workout_id, current_user.id)

    if not workout:
        logger.warning("Тренировка не найдена: ID %d", workout_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )

    return WorkoutResponse.model_validate(workout)


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_data: WorkoutUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkoutResponse:
    updated_workout = await WorkoutService.update_workout(
        db, workout_id, current_user.id, workout_data
    )

    if not updated_workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )

    await db.commit()

    await cache_service.delete_pattern(f"user:{current_user.id}:*")

    return WorkoutResponse.model_validate(updated_workout)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    deleted = await WorkoutService.delete_workout(db, workout_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена",
        )

    await db.commit()

    await cache_service.delete_pattern(f"user:{current_user.id}:*")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
