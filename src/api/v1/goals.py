from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.core.database import get_db
from src.core.logging import get_logger
from src.models.models import User
from src.schemas.goal import GoalCreate, GoalProgress, GoalResponse, GoalUpdate
from src.services.goal_service import GoalService

logger = get_logger(__name__)
router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoalResponse:
    logger.info("Создание цели для пользователя: ID %d", current_user.id)

    goal = await GoalService.create_goal(db, current_user.id, goal_data)
    await db.commit()

    return GoalResponse.model_validate(goal)


@router.get("", response_model=list[GoalResponse])
async def get_goals(
    active_only: Annotated[bool, Query(False)] = False,
    current_user: Annotated[User, Depends(get_current_user)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> list[GoalResponse]:
    goals = await GoalService.get_user_goals(db, current_user.id, active_only)
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoalResponse:
    goal = await GoalService.get_goal_by_id(db, goal_id, current_user.id)

    if not goal:
        logger.warning("Цель не найдена: ID %d", goal_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )

    return GoalResponse.model_validate(goal)


@router.get("/{goal_id}/progress", response_model=GoalProgress)
async def get_goal_progress(
    goal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoalProgress:
    progress = await GoalService.get_goal_progress(db, goal_id, current_user.id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )

    return progress


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoalResponse:
    updated_goal = await GoalService.update_goal(db, goal_id, current_user.id, goal_data)

    if not updated_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )

    await db.commit()

    return GoalResponse.model_validate(updated_goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    deleted = await GoalService.delete_goal(db, goal_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Цель не найдена",
        )

    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
