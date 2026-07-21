from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.auth_token import AuthToken
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import LoginRequest, Token, RefreshRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_token,
)

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже занят")
    
    result = await db.execute(select(User).where(User.nickname == user_data.nickname))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Никнейм уже занят")
    
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        nickname=user_data.nickname,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    refresh_token = generate_refresh_token()
    expires_days = 30 if credentials.remember_me else 1

    db.add(
        AuthToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            remember_me=credentials.remember_me,
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_days),
        )
    )
    await db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(select(AuthToken).where(AuthToken.token_hash == token_hash))
    stored_token = result.scalar_one_or_none()

    if stored_token is None or stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший refresh token",
        )

    access_token = create_access_token({"sub": str(stored_token.user_id)})
    return Token(access_token=access_token, refresh_token=data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(select(AuthToken).where(AuthToken.token_hash == token_hash))
    stored_token = result.scalar_one_or_none()

    if stored_token is not None:
        await db.delete(stored_token)
        await db.commit()