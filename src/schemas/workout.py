from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.models import WorkoutType


class WorkoutBase(BaseModel):
    workout_type: WorkoutType
    duration_minutes: float = Field(gt=0, le=1440)
    distance_km: float | None = Field(None, ge=0)
    average_heart_rate: int | None = Field(None, ge=30, le=250)
    max_heart_rate: int | None = Field(None, ge=30, le=250)
    steps: int | None = Field(None, ge=0)
    pool_length_m: float | None = Field(None, gt=0)
    pool_laps: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=1000)
    started_at: datetime


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    workout_type: WorkoutType | None = None
    duration_minutes: float | None = Field(None, gt=0, le=1440)
    distance_km: float | None = Field(None, ge=0)
    average_heart_rate: int | None = Field(None, ge=30, le=250)
    max_heart_rate: int | None = Field(None, ge=30, le=250)
    steps: int | None = Field(None, ge=0)
    pool_length_m: float | None = Field(None, gt=0)
    pool_laps: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=1000)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class WorkoutResponse(WorkoutBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    calories_burned: float | None = None
    avg_speed_kmh: float | None = None
    completed_at: datetime | None = None
    created_at: datetime


class WorkoutStats(BaseModel):
    total_workouts: int
    total_duration_minutes: float
    total_distance_km: float
    total_calories_burned: float
    average_heart_rate: float | None = None
    favorite_workout_type: str | None = None
