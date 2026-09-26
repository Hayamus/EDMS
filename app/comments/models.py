from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.users.models import User

class Comment(Base, TimestampMixin):

    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]

    document_version_id: Mapped[int] = mapped_column(
        ForeignKey('document_versions.id', ondelete='CASCADE'),
        index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey('users.id')
    )

    author: Mapped['User'] = relationship(lazy='noload')

    def __repr__(self) -> str:
        return f"<Comment id={self.id} document id={self.document_version_id} author id={self.author_id}>"