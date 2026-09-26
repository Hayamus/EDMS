from enum import Enum

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.users.models import User

class NotificationType(str, Enum):
    DOCUMENT_APPROVED = 'document_approved'
    DOCUMENT_REJECTED = 'document_rejected'
    APPROVAL_REQUEST = 'approval_request'
    NEW_COMMENT = 'new_comment'

class Notification(Base, TimestampMixin):

    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name='notification_type', native_enum=True)
    )
    payload: Mapped[dict | None] = mapped_column(JSON)
    is_read: Mapped[bool] = mapped_column(default=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True
    )

    user: Mapped['User'] = relationship(back_populates='notifications', lazy='noload')

    def __repr__(self) -> str:
        return f"<Notification id{self.id} type={self.type} user id{self.user_id}>"