from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.core.database import get_db
from src.core.logging import get_logger
from src.core.security import create_access_token
from src.models.models import User
from src.schemas.user import Token, UserCreate, UserLogin, UserResponse, UserUpdate
from src.services.user_service import UserService

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    logger.info("Попытка регистрации пользователя: %s", user_data.username)

    existing_user = await UserService.get_user_by_username(db, user_data.username)
    if existing_user:
        logger.warning("Пользователь с таким именем уже существует: %s", user_data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )

    existing_email = await UserService.get_user_by_email(db, user_data.email)
    if existing_email:
        logger.warning("Пользователь с таким email уже существует: %s", user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    user = await UserService.create_user(db, user_data)
    await db.commit()
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    logger.info("Попытка входа пользователя: %s", credentials.username)

    user = await UserService.authenticate_user(db, credentials.username, credentials.password)

    if not user:
        logger.warning("Неудачная попытка входа: %s", credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    logger.info("Пользователь успешно вошел: %s", credentials.username)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    logger.info("Обновление профиля пользователя: ID %d", current_user.id)

    updated_user = await UserService.update_user(db, current_user.id, user_data)
    await db.commit()

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return UserResponse.model_validate(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    logger.info("Удаление аккаунта пользователя: ID %d", current_user.id)

    deleted = await UserService.delete_user(db, current_user.id)
    await db.commit()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
