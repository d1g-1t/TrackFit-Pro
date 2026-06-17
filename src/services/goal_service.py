from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.models.models import Goal, Workout
from src.schemas.goal import GoalCreate, GoalProgress, GoalUpdate

logger = get_logger(__name__)


class GoalService:
    @staticmethod
    async def create_goal(db: AsyncSession, user_id: int, goal_data: GoalCreate) -> Goal:
        logger.info("Создание новой цели для пользователя: ID %d", user_id)

        goal = Goal(
            user_id=user_id,
            title=goal_data.title,
            description=goal_data.description,
            target_workouts_per_week=goal_data.target_workouts_per_week,
            target_calories_per_week=goal_data.target_calories_per_week,
            target_distance_km=goal_data.target_distance_km,
            target_weight_kg=goal_data.target_weight_kg,
            deadline=goal_data.deadline,
        )

        db.add(goal)
        await db.flush()
        await db.refresh(goal)

        logger.info("Цель создана успешно: ID %d", goal.id)
        return goal

    @staticmethod
    async def get_goal_by_id(db: AsyncSession, goal_id: int, user_id: int) -> Goal | None:
        result = await db.execute(
            select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == user_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_goals(
        db: AsyncSession, user_id: int, active_only: bool = False
    ) -> list[Goal]:
        query = select(Goal).where(Goal.user_id == user_id)

        if active_only:
            query = query.where(Goal.is_achieved.is_(False))

        query = query.order_by(desc(Goal.created_at))

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_goal(
        db: AsyncSession, goal_id: int, user_id: int, goal_data: GoalUpdate
    ) -> Goal | None:
        logger.info("Обновление цели: ID %d", goal_id)

        goal = await GoalService.get_goal_by_id(db, goal_id, user_id)
        if not goal:
            logger.warning("Цель не найдена: ID %d", goal_id)
            return None

        update_data = goal_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(goal, field, value)

        await db.flush()
        await db.refresh(goal)

        logger.info("Цель обновлена успешно: ID %d", goal_id)
        return goal

    @staticmethod
    async def delete_goal(db: AsyncSession, goal_id: int, user_id: int) -> bool:
        logger.info("Удаление цели: ID %d", goal_id)

        goal = await GoalService.get_goal_by_id(db, goal_id, user_id)
        if not goal:
            logger.warning("Цель не найдена: ID %d", goal_id)
            return False

        await db.delete(goal)
        logger.info("Цель удалена успешно: ID %d", goal_id)
        return True

    @staticmethod
    async def get_goal_progress(
        db: AsyncSession, goal_id: int, user_id: int
    ) -> GoalProgress | None:
        logger.info("Получение прогресса цели: ID %d", goal_id)

        goal = await GoalService.get_goal_by_id(db, goal_id, user_id)
        if not goal:
            return None

        start_date = datetime.now(UTC) - timedelta(days=7)

        result = await db.execute(
            select(
                func.count(Workout.id).label("workout_count"),
                func.coalesce(func.sum(Workout.calories_burned), 0).label("total_calories"),
                func.coalesce(func.sum(Workout.distance_km), 0).label("total_distance"),
            ).where(
                and_(
                    Workout.user_id == user_id,
                    Workout.started_at >= start_date,
                )
            )
        )

        stats = result.one()

        progress = 0.0
        is_on_track = True

        if goal.target_workouts_per_week:
            workout_progress = (stats.workout_count / goal.target_workouts_per_week) * 100
            progress = max(progress, workout_progress)
            is_on_track = is_on_track and (stats.workout_count >= goal.target_workouts_per_week)

        if goal.target_calories_per_week:
            calorie_progress = (stats.total_calories / goal.target_calories_per_week) * 100
            progress = max(progress, calorie_progress)
            is_on_track = is_on_track and (stats.total_calories >= goal.target_calories_per_week)

        if goal.target_distance_km:
            distance_progress = (stats.total_distance / goal.target_distance_km) * 100
            progress = max(progress, distance_progress)
            is_on_track = is_on_track and (stats.total_distance >= goal.target_distance_km)

        return GoalProgress(
            goal_id=goal.id,
            goal_title=goal.title,
            current_workouts=stats.workout_count,
            target_workouts=goal.target_workouts_per_week,
            current_calories=float(stats.total_calories),
            target_calories=goal.target_calories_per_week,
            current_distance=float(stats.total_distance),
            target_distance=goal.target_distance_km,
            progress_percentage=round(min(progress, 100), 2),
            is_on_track=is_on_track,
        )
