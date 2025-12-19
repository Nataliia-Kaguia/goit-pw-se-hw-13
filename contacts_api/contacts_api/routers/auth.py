from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Form, Request
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models, auth as auth_utils
from ..utils_email import send_verification_email, send_reset_email
from ..deps import r
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    user = crud.create_user(db, user_in)
    # send email in background
    background_tasks.add_task(send_verification_email, user.email, user.verification_code)
    return user

@router.get("/verify")
def verify(email: str, code: str, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or user.verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification")
    crud.verify_user(db, user)
    return {"msg": "verified"}

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginData, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user or not auth_utils.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    access, refresh = auth_utils.create_tokens(user.id)
    # cache user in redis for quick access (ttl)
    r.hset(f"user:{user.id}", mapping={"id": user.id, "email": user.email})
    r.expire(f"user:{user.id}", 3600)
    return {"access_token": access, "refresh_token": refresh}

@router.post("/refresh", response_model=schemas.Token)
def refresh(body: schemas.RefreshTokenRequest):
    user_id = auth_utils.verify_refresh_token(body.refresh_token)
    access, refresh = auth_utils.create_tokens(user_id)
    return {"access_token": access, "refresh_token": refresh}
    
@router.post("/forgot-password")
def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        return {"msg": "ok"}
    code = secrets.token_urlsafe(8)
    crud.set_reset_code(db, user, code)
    background_tasks.add_task(send_reset_email, user.email, code)
    return {"msg": "ok"}

@router.post("/reset-password")
def reset_password(email: str, code: str, new_password: str, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or user.reset_code != code:
        raise HTTPException(status_code=400, detail="Invalid code")
    crud.reset_password(db, user, new_password)
    return {"msg": "password reset"}
