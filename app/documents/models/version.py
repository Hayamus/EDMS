from enum import Enum

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.users.models import User, Approval
    from app.documents.models.document import Document
    from app.documents.models.acknowledgement import DocumentAcknowledgement
    from app.comments.models import Comment

class DocumentVersionStatus(str, Enum):
    DRAFT = 'draft'
    PENDING_APPROVAL = 'pending_approval'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    ARCHIVED = 'archived'

class DocumentVersion(Base, TimestampMixin):

    __tablename__ = 'document_versions'

    id: Mapped[int] = mapped_column(primary_key=True)
    version_number: Mapped[int]
    storage_key: Mapped[str]
    status: Mapped[DocumentVersionStatus] = mapped_column(
        SQLEnum(DocumentVersionStatus, name='version_status', native_enum=True),
        default=DocumentVersionStatus.DRAFT
    )
    change_description: Mapped[str | None]

    document_id: Mapped[int] = mapped_column(
        ForeignKey('documents.id', ondelete='CASCADE'),
        index=True
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True
    )

    __table_args__ = (
        UniqueConstraint('document_id', 'version_number', name='uq_document_versions_document_verion'),
    )

    document: Mapped['Document'] = relationship(back_populates='versions', foreign_keys=[document_id], lazy='noload')
    author: Mapped['User'] = relationship(back_populates='created_versions', lazy='noload')
    approvals: Mapped[list['Approval']] = relationship(back_populates='document', lazy='noload', cascade='all, delete-orphan')
    comments: Mapped[list['Comment']] = relationship(lazy='noload', cascade='all, delete-orphan')
    acknowledgements: Mapped[list['DocumentAcknowledgement']] = relationship(
        back_populates='document_version',
        cascade='all, delete-orphan',
        lazy='noload'
    )

    def __repr__(self) -> str:
        return f"<Document version id{self.id} document if{self.document_id} version number{self.version_number}>"