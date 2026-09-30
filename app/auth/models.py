from typing import TYPE_CHECKING
import datetime

from sqlalchemy import Index, func, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.users.models import User

class RefreshToken(Base):

    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_revoked: Mapped[bool] = mapped_column(default=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        index=True
    )

    __table_args__ = (
        Index('ix_user_active_tokens', 'user_id', 'is_revoked'),
    )

    user: Mapped['User'] = relationship(lazy='noload')

    @property
    def is_expired(self) -> bool:
        return datetime.datetime.now(datetime.timezone.utc) >= self.expires_at
    
    def __repr__(self) -> str:
        return f"<Token hash={self.token_hash} user id={self.user_id} is revoked={self.is_revoked}>"