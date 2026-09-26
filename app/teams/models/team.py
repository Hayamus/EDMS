from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.teams.models.team_member import TeamMember
    from app.documents.models.document import Document

class Team(Base, TimestampMixin):

    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    team_documents: Mapped[list['Document']] = relationship(back_populates='team', lazy='noload')
    team_memberships: Mapped[list['TeamMember']] = relationship(back_populates='team', lazy='noload', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Team id={self.id} name={self.name}>"