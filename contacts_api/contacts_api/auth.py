from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from .config import JWT_SECRET, JWT_ALGORITHM, ACCESS_EXPIRE_MINUTES, REFRESH_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_tokens(user_id: int):
    now = datetime.utcnow()
    access_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=ACCESS_EXPIRE_MINUTES),
        "type": "access"
    }
    refresh_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=REFRESH_EXPIRE_MINUTES),
        "type": "refresh"
    }
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return access_token, refresh_token

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def verify_refresh_token(token: str) -> int:
    """
    Перевірка refresh токена та повернення user_id.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        return int(payload["sub"])

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
