from enum import Enum

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import JSON, func, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.users.models import User

class AuditEntityType(str, Enum):
    USER = "user"
    TEAM = "team"
    DOCUMENT = "document"
    DOCUMENT_VERSION = "document_version"
    COMMENT = "comment"
    APPROVAL = "approval"
    ACKNOWLEDGEMENT = "acknowledgement"

class AuditAction(str, Enum):
    USER_REGISTERED = "user_registered"
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGIN_FAILED = "user_login_failed"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    USER_TOKEN_REFRESHED = "user_token_refreshed"
    USER_LOGGED_OUT = "user_logged_out"

    TEAM_MEMBER_ADDED = "team_member_added"
    TEAM_MEMBER_REMOVED = "team_member_removed"

    DOCUMENT_CREATED = "document_created"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    DOCUMENT_ARCHIVED = "document_archived"

    VERSION_UPLOADED = "version_uploaded"

    COMMENT_ADDED = "comment_added"
    COMMENT_DELETED = "comment_deleted"

    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"

    DOCUMENT_ACKNOWLEDGED = "document_acknowledged"

class AuditLog(Base):

    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int | None]
    entity_type: Mapped[AuditEntityType] = mapped_column(
        SQLEnum(AuditEntityType, name='audit_entity_type', native_enum=True)
    )
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction, name='audit_action', native_enum=True)
    )
    details: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'),
        index=True
    )

    __table_args__ = (
        Index('ix_audit_entity', 'entity_type', 'entity_id'),
    )
    
    user: Mapped['User | None'] = relationship(lazy='noload')


    def __repr__(self) -> str:
        return f"<action={self.action} entity type={self.entity_type} entity id={self.entity_id} details={self.details}>"