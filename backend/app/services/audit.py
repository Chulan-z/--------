import logging

from sqlalchemy.orm import Session

from app.models.log import Log

logger = logging.getLogger("news_aggregator")


def write_log(
    db: Session,
    *,
    action: str,
    entity: str,
    message: str,
    level: str = "info",
    user_id: int | None = None,
    ip_address: str | None = None,
) -> Log:
    """Единая точка аудита действий пользователей, администраторов и системных операций."""
    record = Log(
        user_id=user_id,
        action=action,
        entity=entity,
        level=level,
        message=message,
        ip_address=ip_address,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    getattr(logger, "error" if level == "error" else "warning" if level == "warning" else "info")(message)
    return record
