from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ..database import get_db
from ..utils_cloudinary import upload_avatar

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/me/avatar")
async def upload_me_avatar(file: UploadFile = File(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    content = await file.read()
    url = upload_avatar(content, f"user_{user.id}_avatar")
    # update user
    user.avatar_url = url
    db.add(user); db.commit(); db.refresh(user)
    return {"avatar_url": url}
