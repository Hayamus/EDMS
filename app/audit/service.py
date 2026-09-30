from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditAction, AuditEntityType, AuditLog

async def log_action(
    db: AsyncSession,
    *,
    user_id: int | None,
    action: AuditAction,
    entity_type: AuditEntityType,
    entity_id: int | None = None,
    details: dict | None = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(entry)