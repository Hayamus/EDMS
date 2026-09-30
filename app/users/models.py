from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.teams.models.team_member import TeamMember
    from app.documents.models.document import DocumentVersion, Document
    from app.documents.models.acknowledgement import DocumentAcknowledgement
    from app.approvals.models import Approval
    from app.notifications.models import Notification

class User(Base, TimestampMixin):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    authored_documents: Mapped[list['Document']] = relationship(back_populates='author', lazy='noload')
    team_memberships: Mapped[list['TeamMember']] = relationship(back_populates='user', lazy='noload')
    notifications: Mapped[list['Notification']] = relationship(back_populates='user', lazy='noload')
    created_versions: Mapped[list['DocumentVersion']] = relationship(back_populates='author', lazy='noload')
    approvals: Mapped[list['Approval']] = relationship(back_populates='approver', lazy='noload')
    acknowledgements: Mapped[list['DocumentAcknowledgement']] = relationship(back_populates='user', lazy='noload')

    def __repr__(self) -> str:
        return f'<User id={self.id} email={self.email!r} is_admin={self.is_admin}>'