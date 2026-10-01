from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import log_action
from app.audit.models import AuditAction, AuditEntityType
from app.core.exceptions import TeamAlreadyExistsException, UserNotFoundException, TeamNotFoundException, UserAlreadyInThisTeamException, UserAlreadyHasThisRoleException
from app.teams.models.team import Team
from app.teams.models.team_member import TeamMember, UserRole
from app.users.models import User

async def create_team(db: AsyncSession, team_name: str, user_id: int) -> Team:
    existing = await db.scalar(select(Team).where(Team.name == team_name))
    if existing is not None:
        raise TeamAlreadyExistsException()

    team = Team(
        name=team_name,
    )
    db.add(team)
    await db.flush()

    team_member = TeamMember(
        user_id=user_id,
        team_id=team.id,
        role=UserRole.MANAGER,
    )
    db.add(team_member)

    await db.commit()
    await db.refresh(team)

    return team

async def add_member(db: AsyncSession, member_id: int, team_id: int, admin_id: int) -> TeamMember:
    existing_user = await db.scalar(select(User).where(User.id == member_id))
    if existing_user is None:
        raise UserNotFoundException()
        
    existing_team = await db.scalar(select(Team).where(Team.id == team_id))
    if existing_team is None:
        raise TeamNotFoundException()

    user_already_in_team = await db.scalar(select(TeamMember).where(TeamMember.user_id == member_id, TeamMember.team_id == team_id))
    if user_already_in_team is not None:
        raise UserAlreadyInThisTeamException()

    team_member = TeamMember(
        user_id=member_id,
        team_id=team_id,
        role=UserRole.EMPLOYEE,
    )
    db.add(team_member)

    await log_action(
        db,
        user_id=admin_id,
        action=AuditAction.TEAM_MEMBER_ADDED,
        entity_type=AuditEntityType.TEAM,
        entity_id=team_id,
        details={
            'member_id': member_id
        }
    )

    await db.commit()
    await db.refresh(team_member)

    return team_member

async def change_member_role(db: AsyncSession, member_id: int, team_id: int, new_role: UserRole, admin_id: int) -> TeamMember:
    team_member = await db.scalar(select(TeamMember).where(TeamMember.user_id == member_id, TeamMember.team_id == team_id))
    if team_member is None:
        raise UserNotFoundException()

    if team_member.role == new_role:
        raise UserAlreadyHasThisRoleException()

    team_member.role = new_role

    await log_action(
        db,
        user_id=admin_id,
        action=AuditAction.TEAM_MEMBER_ROLE_CHANGED,
        entity_type=AuditEntityType.TEAM,
        entity_id=team_id,
        details={
            'member_id': member_id,
            'new_role': new_role
        }
    )
    await db.commit()
    await db.refresh(team_member)

    return team_member

async def list_teams(db: AsyncSession) -> list[Team]:
    result = await db.execute(select(Team).order_by(Team.name))
    return list(result.scalars().all())

async def list_team_members(db: AsyncSession, team_id: int) -> list[TeamMember]:
    if await db.get(Team, team_id) is None:
        raise TeamNotFoundException()

    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.team_id == team_id)
        .options(selectinload(TeamMember.user))
        .order_by(TeamMember.role)
    )
    return list(result.scalars().all())