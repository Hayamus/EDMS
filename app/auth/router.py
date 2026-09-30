from fastapi import APIRouter, Depends, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.schemas import RegisterIn, UserOut, AccessTokenOut
from app.audit.models import AuditAction
from app.core.config import settings
from app.core.exceptions import RefreshTokenInvalidException
from app.db.session import get_db

router = APIRouter(prefix='/auth', tags=['auth'])

def _set_refresh_cookie(response: Response, raw_refresh_token: str, expires_at) -> None:
    response.set_cookie(
        key='refresh_token',
        value=raw_refresh_token,
        httponly=True,
        secure=not settings.debug,
        samesite='lax',
        expires=expires_at,
        path='/auth'
    )

@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await service.register_user(db, data)
    return user

@router.post('/login', response_model=AccessTokenOut)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> AccessTokenOut:
    user = await service.authenticate_user(db, form_data.username, form_data.password)
    access_token, raw_refresh, expires_at = await service.issue_tokens(db, user, AuditAction.USER_LOGGED_IN)

    _set_refresh_cookie(response, raw_refresh, expires_at)

    return AccessTokenOut(access_token=access_token)

@router.post('/refresh', response_model=AccessTokenOut)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> AccessTokenOut:
    if refresh_token is None:
        raise RefreshTokenInvalidException()

    access_token, raw_new_refresh, expires_at = await service.rotate_refresh_token(db, refresh_token)
    _set_refresh_cookie(response, raw_new_refresh, expires_at)

    return AccessTokenOut(access_token=access_token)

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> None:
    if refresh_token is not None:
        await service.revoke_refresh_token(db, refresh_token)

    response.delete_cookie(key='refresh_token', path='/auth')