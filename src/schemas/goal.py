from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GoalBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    target_workouts_per_week: int | None = Field(None, ge=1, le=50)
    target_calories_per_week: float | None = Field(None, gt=0)
    target_distance_km: float | None = Field(None, gt=0)
    target_weight_kg: float | None = Field(None, gt=0, le=500)
    deadline: datetime | None = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    target_workouts_per_week: int | None = Field(None, ge=1, le=50)
    target_calories_per_week: float | None = Field(None, gt=0)
    target_distance_km: float | None = Field(None, gt=0)
    target_weight_kg: float | None = Field(None, gt=0, le=500)
    deadline: datetime | None = None
    is_achieved: bool | None = None


class GoalResponse(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_achieved: bool
    created_at: datetime
    updated_at: datetime


class GoalProgress(BaseModel):
    goal_id: int
    goal_title: str
    current_workouts: int
    target_workouts: int | None = None
    current_calories: float
    target_calories: float | None = None
    current_distance: float
    target_distance: float | None = None
    progress_percentage: float
    is_on_track: bool
