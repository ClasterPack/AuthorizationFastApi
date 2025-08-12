from datetime import datetime, timezone

import bcrypt
import jwt
from asyncpg.pgproto.pgproto import timedelta
from fastapi import HTTPException, Request, status

from src.core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.private_key,
    algorithm: str = settings.algorithm,
    exp_days: int = None,
):

    to_encode = payload.copy()
    iat = datetime.now(timezone.utc)

    expire_in_minutes = (
        settings.access_token_expire_minutes if not exp_days else exp_days * 1440
    )
    exp = iat + timedelta(minutes=expire_in_minutes)
    to_encode.update(exp=exp, iat=iat)
    encoded = jwt.encode(to_encode, key=private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    key: str = settings.public_key,
    algorithm: str = settings.algorithm,
) -> dict:
    decoded = jwt.decode(token, key, algorithms=[algorithm])
    return decoded


def hash_pwd(
    password: str,
) -> str:
    pass_bytes = password.strip().encode("utf-8")
    hashes_pass = bcrypt.hashpw(pass_bytes, bcrypt.gensalt())
    return hashes_pass.decode("utf-8")


def validate_pwd(password_raw: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password_raw.strip().encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or malformed",
        )
    token = auth_header[7:]
    try:
        payload = decode_jwt(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
