from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.core.security import get_password_hash, verify_password
from src.models.models import User
from src.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        logger.info("Создание нового пользователя: %s", user_data.username)

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            age=user_data.age,
            weight=user_data.weight,
            height=user_data.height,
            gender=user_data.gender,
        )

        db.add(user)
        await db.flush()
        await db.refresh(user)

        logger.info("Пользователь создан успешно: ID %d", user.id)
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        logger.info("Попытка аутентификации пользователя: %s", username)

        user = await UserService.get_user_by_username(db, username)

        if not user:
            logger.warning("Пользователь не найден: %s", username)
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning("Неверный пароль для пользователя: %s", username)
            return None

        logger.info("Пользователь успешно аутентифицирован: %s", username)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User | None:
        logger.info("Обновление данных пользователя: ID %d", user_id)

        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            logger.warning("Пользователь не найден для обновления: ID %d", user_id)
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)

        logger.info("Пользователь обновлен успешно: ID %d", user_id)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        logger.info("Удаление пользователя: ID %d", user_id)

        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            logger.warning("Пользователь не найден для удаления: ID %d", user_id)
            return False

        await db.delete(user)
        logger.info("Пользователь удален успешно: ID %d", user_id)
        return True
