from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.teams.models.team import Team
    from app.users.models import User
    from app.documents.models.version import DocumentVersion

class Document(Base, TimestampMixin):

    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None]

    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'))
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey('document_versions.id', use_alter=True, name='fk_document_current_version'),
        nullable=True
        )

    team: Mapped['Team'] = relationship(back_populates='team_documents', lazy='noload')
    author: Mapped['User'] = relationship(back_populates='authored_documents', lazy='noload')
    versions: Mapped[list['DocumentVersion']] = relationship(
        back_populates='document',
        cascade='all, delete-orphan',
        lazy='noload',
        foreign_keys='DocumentVersion.document_id',
        order_by='DocumentVersion.version_number'
    )
    current_version: Mapped['DocumentVersion | None'] = relationship(
        foreign_keys=[current_version_id],
        lazy='noload',
        post_update=True
    )

    def __repr__(self) -> str:
        return f"<Document id{self.id} title{self.title}>"