from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.users.models import DocumentVersion, User

class DocumentAcknowledgement(Base, TimestampMixin):

    __tablename__ = 'document_acknowledgements'

    id: Mapped[int] = mapped_column(primary_key=True)
    is_acknowledged: Mapped[bool] = mapped_column(default=False)

    document_version_id: Mapped[int] = mapped_column(
        ForeignKey('document_versions.id', ondelete='CASCADE'),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True
    )

    __table_args__ = (
        UniqueConstraint('document_version_id', 'user_id', name='uq_document_acknowledgements_user_verion'),
    )

    document_version: Mapped['DocumentVersion'] = relationship(back_populates="acknowledgements", lazy='noload')
    user: Mapped['User'] = relationship(back_populates="acknowledgements", lazy='noload')

    def __repr__(self) -> str:
        return f"<Document version id{self.document_version_id} user id{self.user_id} is acknowledged{self.is_acknowledged}>"