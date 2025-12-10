from sqlalchemy.orm import Session
from . import models, schemas, auth
import secrets

def create_user(db: Session, user_in: schemas.UserCreate):
    hashed = auth.hash_password(user_in.password)
    code = secrets.token_urlsafe(16)
    user = models.User(email=user_in.email, hashed_password=hashed, verification_code=code)
    db.add(user); db.commit(); db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def verify_user(db: Session, user: models.User):
    user.is_verified = True
    user.verification_code = None
    db.commit(); db.refresh(user)
    return user

def set_reset_code(db: Session, user: models.User, code: str):
    user.reset_code = code
    db.commit()

def reset_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = auth.hash_password(new_password)
    user.reset_code = None
    db.commit()
