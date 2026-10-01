from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token, TokenExpiredError, InvalidTokenError
from app.db.session import get_db
from app.teams.models.team_member import TeamMember, UserRole
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if payload.get('type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')

    user_id = int(payload['sub'])
    user = await db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found or inactive')

    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin Only')
    return current_user

async def ensure_team_role(
        db: AsyncSession,
        user: User,
        team_id: int,
        allowed: set[UserRole],
) -> TeamMember:
    membership = await db.scalar(
        select(TeamMember).where(
            TeamMember.user_id == user.id,
            TeamMember.team_id == team_id,
            )
    )

    if user.is_admin:
        return membership

    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a member')

    if membership.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough role')

    return membership

def require_team_role(*allowed: UserRole):
    async def dependency(
            team_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
    ) -> User:
        await ensure_team_role(db, current_user, team_id, set(allowed))
        return current_user
    return dependency