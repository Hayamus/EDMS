from enum import Enum

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.documents.models.version import User, DocumentVersion

class ApprovalStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class Approval(Base, TimestampMixin):

    __tablename__ = 'approvals'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[ApprovalStatus] = mapped_column(
        SQLEnum(ApprovalStatus, name='approval_status', native_enum=True),
        default=ApprovalStatus.PENDING
    )
    comment: Mapped[str]
    approved_at: Mapped[datetime] = mapped_column(server_default=func.now())

    document_version_id: Mapped[int] = mapped_column(
        ForeignKey('document_versions.id', ondelete='CASCADE'),
        index=True
    )
    approver_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True
    )

    __table_args__ = (
        UniqueConstraint('document_version_id', 'approver_id', name='uq_approvals_version_approver'),
    )

    approver: Mapped['User'] = relationship(back_populates='approvals', lazy='noload')
    document: Mapped['DocumentVersion'] = relationship(back_populates='approvals', lazy='noload')

    def __repr__(self) -> str:
        return f"<Approval id={self.id} status={self.status} document id={self.document_version_id} approver={self.approver_id}>"