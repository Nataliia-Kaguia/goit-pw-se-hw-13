from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from . import auth, models
from fastapi.security import HTTPBearer
from jose import JWTError
from .config import REDIS_URL
import redis

sec = HTTPBearer()

r = redis.from_url(REDIS_URL, decode_responses=True)

def get_current_user(token=Depends(sec), db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(token.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # cache user in redis (simple)
    r.hset(f"user:{user_id}", mapping={"id": user.id, "email": user.email})
    return user
