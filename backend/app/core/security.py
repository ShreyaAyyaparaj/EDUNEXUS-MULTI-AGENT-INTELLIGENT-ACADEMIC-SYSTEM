from datetime import datetime, timedelta, timezone
from typing import Any
import hashlib
import hmac

import jwt
from pwdlib import PasswordHash

from app.db.database import settings


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    # Compatibility with the existing synthetic seed accounts.
    if (
        len(hashed_password) == 64
        and all(c in "0123456789abcdef" for c in hashed_password.lower())
    ):
        candidate = hashlib.sha256(
            plain_password.encode("utf-8")
        ).hexdigest()

        return hmac.compare_digest(
            candidate,
            hashed_password.lower(),
        )

    try:
        return password_hasher.verify(
            plain_password,
            hashed_password,
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
