from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import logging

from app.auth.schemas import RegisterIn, LoginIn
from app.auth.models import RefreshToken
from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException, RefreshTokenInvalidException
from app.core.security import hash_password, verify_password, create_access_token, generate_refresh_token, hash_token
from app.users.models import User
from app.audit.service import log_action
from app.audit.models import AuditAction, AuditEntityType

logger = logging.getLogger(__name__)

async def register_user(db: AsyncSession, data: RegisterIn) -> User:
    existing = await db.scalar(select(User).where(User.email == data.email))
    if existing is not None:
        raise UserAlreadyExistsException()

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.flush()

    await log_action(
        db,
        user_id=user.id,
        action=AuditAction.USER_REGISTERED,
        entity_type=AuditEntityType.USER,
        entity_id=user.id,
    )

    await db.commit()
    await db.refresh(user)

    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(password, user.password_hash) or not user.is_active:
        logger.warning(f'Failed login attempt for email={email}')
        await log_action(
            db,
            user_id=user.id if user else None,
            action=AuditAction.USER_LOGIN_FAILED,
            entity_type=AuditEntityType.USER,
            entity_id=user.id if user else None,
            details={'email': email},
        )
        await db.commit()
        raise InvalidCredentialsException()

    return user

async def issue_tokens(db: AsyncSession, user: User, action: AuditAction) -> tuple[str, str, datetime]:
    access_token = create_access_token(subject=user.id)

    raw_refresh, refresh_hash, expires_at = generate_refresh_token()
    db.add(RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=expires_at))

    await log_action(
        db,
        user_id=user.id,
        action=action,
        entity_type=AuditEntityType.USER,
        entity_id=user.id,
    )

    await db.commit()

    return access_token, raw_refresh, expires_at

async def rotate_refresh_token(db: AsyncSession, raw_refresh_token: str) -> tuple[str, str, datetime]:
    token_hash = hash_token(raw_refresh_token)

    stored_token = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,  # noqa: E712
        )
    )

    if stored_token is None or stored_token.expires_at < datetime.now(timezone.utc):
        raise RefreshTokenInvalidException()

    user = await db.get(User, stored_token.user_id)
    if user is None or not user.is_active:
        raise RefreshTokenInvalidException()

    stored_token.is_revoked = True

    access_token, raw_new_refresh, expires_at = await issue_tokens(
        db, user, AuditAction.USER_TOKEN_REFRESHED
    )

    return access_token, raw_new_refresh, expires_at

async def revoke_refresh_token(db: AsyncSession, raw_refresh_token: str) -> None:
    token_hash = hash_token(raw_refresh_token)

    stored_token = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )

    if stored_token is None:
        return 

    stored_token.is_revoked = True

    await log_action(
        db,
        user_id=stored_token.user_id,
        action=AuditAction.USER_LOGGED_OUT,
        entity_type=AuditEntityType.USER,
        entity_id=stored_token.user_id,
    )

    await db.commit()