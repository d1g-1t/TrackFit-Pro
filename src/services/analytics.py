from src.models.models import WorkoutType


class TrainingConstants:
    LEN_STEP = 0.65
    M_IN_KM = 1000
    MIN_IN_H = 60
    SWIMMING_LEN_STEP = 1.38

    RUNNING_CALORIES_MEAN_SPEED_MULTIPLIER = 18
    RUNNING_CALORIES_MEAN_SPEED_SHIFT = 1.79

    WALKING_CALORIES_WEIGHT_MULTIPLIER = 0.035
    WALKING_CALORIES_SPEED_HEIGHT_MULTIPLIER = 0.029
    WALKING_KMH_IN_MSEC = 0.278
    WALKING_CM_IN_M = 100

    SWIMMING_CALORIES_MEAN_SPEED_SHIFT = 1.1
    SWIMMING_CALORIES_WEIGHT_MULTIPLIER = 2


class CalorieCalculator:
    RUNNING_MET = 9.8
    WALKING_MET = 3.8
    SWIMMING_MET = 8.0
    CYCLING_MET = 7.5
    STRENGTH_MET = 6.0
    YOGA_MET = 2.5
    DEFAULT_MET = 5.0

    @staticmethod
    def calculate_calories(
        workout_type: WorkoutType,
        duration_minutes: float,
        weight_kg: float,
        avg_speed_kmh: float | None = None,
    ) -> float:
        match workout_type:
            case WorkoutType.RUNNING:
                met = CalorieCalculator._get_running_met(avg_speed_kmh)
            case WorkoutType.WALKING:
                met = CalorieCalculator._get_walking_met(avg_speed_kmh)
            case WorkoutType.SWIMMING:
                met = CalorieCalculator.SWIMMING_MET
            case WorkoutType.CYCLING:
                met = CalorieCalculator._get_cycling_met(avg_speed_kmh)
            case WorkoutType.STRENGTH:
                met = CalorieCalculator.STRENGTH_MET
            case WorkoutType.YOGA:
                met = CalorieCalculator.YOGA_MET
            case _:
                met = CalorieCalculator.DEFAULT_MET

        duration_hours = duration_minutes / 60
        return round(met * weight_kg * duration_hours, 2)

    @staticmethod
    def _get_running_met(avg_speed_kmh: float | None = None) -> float:
        if not avg_speed_kmh:
            return CalorieCalculator.RUNNING_MET
        if avg_speed_kmh < 8:
            return 8.0
        if avg_speed_kmh < 10:
            return 9.8
        if avg_speed_kmh < 12:
            return 11.0
        if avg_speed_kmh < 14:
            return 11.8
        return 14.5

    @staticmethod
    def _get_walking_met(avg_speed_kmh: float | None = None) -> float:
        if not avg_speed_kmh:
            return CalorieCalculator.WALKING_MET
        if avg_speed_kmh < 4:
            return 2.8
        if avg_speed_kmh < 5:
            return 3.5
        if avg_speed_kmh < 6:
            return 4.3
        return 5.0

    @staticmethod
    def _get_cycling_met(avg_speed_kmh: float | None = None) -> float:
        if not avg_speed_kmh:
            return CalorieCalculator.CYCLING_MET
        if avg_speed_kmh < 16:
            return 4.0
        if avg_speed_kmh < 20:
            return 6.8
        if avg_speed_kmh < 25:
            return 8.0
        return 10.0


class WorkoutAnalytics:
    @staticmethod
    def calculate_distance_from_steps(steps: int, workout_type: WorkoutType) -> float:
        step_length = (
            TrainingConstants.SWIMMING_LEN_STEP
            if workout_type == WorkoutType.SWIMMING
            else TrainingConstants.LEN_STEP
        )
        return round(steps * step_length / TrainingConstants.M_IN_KM, 3)

    @staticmethod
    def calculate_average_speed(distance_km: float, duration_minutes: float) -> float:
        if duration_minutes <= 0:
            return 0.0
        return round(distance_km / (duration_minutes / 60), 2)

    @staticmethod
    def calculate_swimming_distance(pool_length_m: float, pool_laps: int) -> float:
        return round(pool_length_m * pool_laps / 1000, 3)

    @staticmethod
    def estimate_steps(distance_km: float, workout_type: WorkoutType) -> int:
        avg_step_length = {
            WorkoutType.RUNNING: 0.00078,
            WorkoutType.WALKING: 0.00065,
        }
        step_length = avg_step_length.get(workout_type)
        if not step_length:
            return 0
        return int(distance_km / step_length)

    @staticmethod
    def calculate_heart_rate_zones(max_hr: int) -> dict[str, dict[str, int]]:
        return {
            "zone1_recovery": {"min": int(max_hr * 0.5), "max": int(max_hr * 0.6)},
            "zone2_endurance": {"min": int(max_hr * 0.6), "max": int(max_hr * 0.7)},
            "zone3_tempo": {"min": int(max_hr * 0.7), "max": int(max_hr * 0.8)},
            "zone4_threshold": {"min": int(max_hr * 0.8), "max": int(max_hr * 0.9)},
            "zone5_max": {"min": int(max_hr * 0.9), "max": max_hr},
        }

    @staticmethod
    def calculate_running_calories_precise(
        action: int, duration_hours: float, weight_kg: float
    ) -> float:
        distance_km = action * TrainingConstants.LEN_STEP / TrainingConstants.M_IN_KM
        avg_speed_kmh = distance_km / duration_hours
        return (
            (
                TrainingConstants.RUNNING_CALORIES_MEAN_SPEED_MULTIPLIER * avg_speed_kmh
                + TrainingConstants.RUNNING_CALORIES_MEAN_SPEED_SHIFT
            )
            * weight_kg
            / TrainingConstants.M_IN_KM
            * duration_hours
            * TrainingConstants.MIN_IN_H
        )

    @staticmethod
    def calculate_walking_calories_precise(
        action: int, duration_hours: float, weight_kg: float, height_cm: float
    ) -> float:
        distance_km = action * TrainingConstants.LEN_STEP / TrainingConstants.M_IN_KM
        avg_speed_kmh = distance_km / duration_hours
        speed_ms = avg_speed_kmh * TrainingConstants.WALKING_KMH_IN_MSEC
        height_m = height_cm / TrainingConstants.WALKING_CM_IN_M
        return (
            (
                TrainingConstants.WALKING_CALORIES_WEIGHT_MULTIPLIER * weight_kg
                + (speed_ms**2 / height_m)
                * TrainingConstants.WALKING_CALORIES_SPEED_HEIGHT_MULTIPLIER
                * weight_kg
            )
            * duration_hours
            * TrainingConstants.MIN_IN_H
        )

    @staticmethod
    def calculate_swimming_calories_precise(
        pool_length_m: float,
        pool_laps: int,
        duration_hours: float,
        weight_kg: float,
    ) -> float:
        distance_km = (pool_length_m * pool_laps) / TrainingConstants.M_IN_KM
        avg_speed_kmh = distance_km / duration_hours
        return (
            (avg_speed_kmh + TrainingConstants.SWIMMING_CALORIES_MEAN_SPEED_SHIFT)
            * TrainingConstants.SWIMMING_CALORIES_WEIGHT_MULTIPLIER
            * weight_kg
            * duration_hours
        )
