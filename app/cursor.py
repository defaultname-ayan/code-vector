import base64
from datetime import datetime, timezone


DELIMITER = "|"


def encode_cursor(session_start: datetime, last_created_at: datetime, last_id: int) -> str:
    raw = DELIMITER.join([
        session_start.isoformat(),
        last_created_at.isoformat(),
        str(last_id),
    ])
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, datetime, int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        parts = raw.split(DELIMITER)
        session_start = datetime.fromisoformat(parts[0])
        last_created_at = datetime.fromisoformat(parts[1])
        last_id = int(parts[2])
        return session_start, last_created_at, last_id
    except Exception:
        raise ValueError("Invalid cursor")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
