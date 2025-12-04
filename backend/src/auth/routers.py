"""
Authentication and user management routes.

Provides endpoints for user registration, login, token refresh, logout,
and user profile retrieval. Uses JWT tokens stored in HTTP-only cookies
for authentication.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.mappers import user_to_read
from src.auth.models import Role, User
from src.auth.schemas import LoginForm, RegisterForm, UserRead
from src.auth.utils.passwords import hash_password, verify_password
from src.database import get_async_session
from src.dependencies import AuthDep, DBSessionDep, RefreshDep, auth


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(
    data: RegisterForm,
    response: Response,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Register a new user account with email and password.
    
    Creates a new user with GUEST role, generates JWT access and refresh tokens,
    and sets them as HTTP-only cookies in the response.
    
    Args:
        data: Registration form containing email, password, first name, last name, and username.
        response: FastAPI Response object for setting authentication cookies.
        db: Database session for user creation.
    
    Returns:
        Dictionary containing success message and created user ID.
    
    Raises:
        HTTPException 400: If user with provided email already exists.
    """
    exists = await db.scalar(select(User).where(User.email == data.email))
    if exists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        hashed_password=hash_password(data.password),
        is_active=True,
        role=Role.GUEST,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access = auth.create_access_token(uid=str(user.id), fresh=True)
    refresh = auth.create_refresh_token(uid=str(user.id))
    auth.set_access_cookies(access, response)
    auth.set_refresh_cookies(refresh, response)

    return {"msg": "Регистрация успешна", "user_id": user.id}


@router.post(
    "/login",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Вход (login)"
)
async def login(
    data: LoginForm,
    response: Response,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Authenticate user and issue JWT tokens.
    
    Verifies user credentials and sets fresh access and refresh tokens
    as HTTP-only cookies in the response.
    
    Args:
        data: Login form containing email and password.
        response: FastAPI Response object for setting authentication cookies.
        db: Database session for user lookup.
    
    Returns:
        None (204 No Content on success).
    
    Raises:
        HTTPException 401: If email or password is incorrect.
    """
    user = await db.scalar(select(User).where(User.email == data.email))
    if not user or not await verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    access = auth.create_access_token(uid=str(user.id), fresh=True)
    refresh = auth.create_refresh_token(uid=str(user.id))
    auth.set_access_cookies(access, response)
    auth.set_refresh_cookies(refresh, response)
    return


@router.post(
    "/refresh",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить access‑токен"
)
async def refresh_token(
    response: Response,
    payload: RefreshDep,
):
    """
    Issue new access token using valid refresh token.
    
    Validates the refresh token from cookies and generates new access
    and refresh tokens, updating the authentication cookies.
    
    Args:
        response: FastAPI Response object for setting updated cookies.
        payload: Decoded refresh token payload containing user ID.
    
    Returns:
        None (204 No Content on success).
    
    Raises:
        HTTPException 401: If refresh token is invalid or expired (handled by RefreshDep).
    """
    new_access = auth.create_access_token(uid=payload.sub, fresh=True)
    refresh = auth.create_refresh_token(uid=str(payload.sub))
    auth.set_access_cookies(new_access, response)
    auth.set_refresh_cookies(refresh, response)
    return


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """
    Log out user by clearing authentication cookies.
    
    Removes access and refresh token cookies from the client browser,
    effectively logging out the user.
    
    Args:
        response: FastAPI Response object for unsetting cookies.
    
    Returns:
        None (204 No Content).
    
    Note:
        This only clears cookies on the client side. Tokens remain valid
        until expiration if stored elsewhere.
    """
    auth.unset_access_cookies(response)
    auth.unset_refresh_cookies(response)


@router.get("/users", response_model=UserRead)
async def get_user(
    db_session: DBSessionDep,
    payload: AuthDep
) -> UserRead:
    """
    Retrieve current authenticated user profile.
    
    Fetches user data based on the JWT token payload. Requires valid
    access token in cookies.
    
    Args:
        db_session: Database session for querying user data.
        payload: Decoded JWT payload containing authenticated user ID.
    
    Returns:
        UserRead object with user profile information.
    
    Raises:
        HTTPException 401: If user is not found in database or token is invalid.
    """
    user_id = UUID(payload.sub)
    stmt = (
        select(User)
        .where(User.id == user_id)
    )

    user: User | None = (await db_session.execute(stmt)).scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user_to_read(user)
