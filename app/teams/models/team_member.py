from typing import TYPE_CHECKING

from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.users.models import User
    from app.teams.models.team import Team

class UserRole(str, Enum):
    EMPLOYEE = 'employee'
    MANAGER = 'manager'
    APPROVER = 'approver'

class TeamMember(Base, TimestampMixin):

    __tablename__ = 'team_members'

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id', ondelete='CASCADE'), index=True)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name='user_role', native_enum=True),
        default=UserRole.EMPLOYEE
        )

    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='uq_team_members_user_team'),
    )

    user: Mapped['User'] = relationship(back_populates='team_memberships', lazy='noload')
    team: Mapped['Team'] = relationship(back_populates='team_memberships', lazy='noload')

    def __repr__(self) -> str:
        return f"<Team id={self.team_id} user id={self.user_id} role={self.role}>"