from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

#Добавляет данные колонки всем моделям, которые его наследуют
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )