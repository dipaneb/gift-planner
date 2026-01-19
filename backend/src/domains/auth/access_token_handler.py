from datetime import datetime, timedelta, timezone
from typing import Any

import jwt  # pyjwt

from src.config.settings import get_settings

settings = get_settings()

def create_access_token(*, subject: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
