from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.teams import service
from app.teams.schemas import TeamCreate, TeamMemberWithUserOut, TeamOut, TeamMemberOut, UserRole, AddMember, ChangeRole
from app.db.session import get_db
from app.users.models import User
from app.core.dependencies import require_admin, require_team_role, get_current_user

router = APIRouter(prefix='/teams', tags=['teams'])

@router.post('', response_model=TeamOut, status_code=status.HTTP_201_CREATED)
async def create(
    data: TeamCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> TeamOut:
    team = await service.create_team(db, data.name, admin.id)
    return team

@router.post('/{team_id}/members', response_model=TeamMemberOut)
async def add(
    team_id: int,
    data: AddMember,
    admin: User = Depends(require_team_role(UserRole.APPROVER, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
) -> TeamMemberOut:
    team_member = await service.add_member(db, data.user_id, team_id, admin.id)
    return team_member

@router.patch('/{team_id}/members/{member_id}', response_model=TeamMemberOut)
async def change(
    member_id: int,
    team_id: int,
    new_role: ChangeRole,
    admin: User = Depends(require_team_role(UserRole.APPROVER, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
) -> TeamMemberOut:
    team_member = await service.change_member_role(db, member_id, team_id, new_role.role, admin.id)
    return team_member

@router.get('', response_model=list[TeamOut])
async def get_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[TeamOut]:
    return await service.list_teams(db)

@router.get('/{team_id}/members', response_model=list[TeamMemberWithUserOut])
async def get_members(
    team_id: int,
    current_user: User = Depends(require_team_role(UserRole.APPROVER, UserRole.MANAGER, UserRole.EMPLOYEE)),
    db: AsyncSession = Depends(get_db)
):
    return await service.list_team_members(db, team_id)