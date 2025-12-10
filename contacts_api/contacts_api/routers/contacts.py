from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_current_user, r
from ..database import get_db
from .. import models, schemas
from ..config import RATE_LIMIT_CREATE, RATE_LIMIT_PERIOD
import time

router = APIRouter(prefix="/contacts", tags=["contacts"])

def check_rate_limit(user_id: int):
    key = f"rate:create:{user_id}"
    now = int(time.time())
    # simple sliding window counter via Redis INCR with expiry
    count = r.incr(key)
    if count == 1:
        r.expire(key, RATE_LIMIT_PERIOD)
    if int(count) > RATE_LIMIT_CREATE:
        return False
    return True

@router.post("/", response_model=schemas.ContactOut, status_code=201)
def create_contact(contact_in: schemas.ContactCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not check_rate_limit(user.id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for creating contacts")
    contact = models.Contact(**contact_in.model_dump(), owner_id=user.id)
    db.add(contact); db.commit(); db.refresh(contact)
    return contact

@router.get("/", response_model=list[schemas.ContactOut])
def list_contacts(user=Depends(get_current_user), db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).filter(models.Contact.owner_id == user.id).all()
    return contacts

@router.get("/{contact_id}", response_model=schemas.ContactOut)
def get_contact(contact_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(models.Contact).filter(models.Contact.id==contact_id, models.Contact.owner_id==user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c

@router.put("/{contact_id}", response_model=schemas.ContactOut)
def update_contact(contact_id: int, contact_in: schemas.ContactCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(models.Contact).filter(models.Contact.id==contact_id, models.Contact.owner_id==user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in contact_in.model_dump().items():
        setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c

@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(models.Contact).filter(models.Contact.id==contact_id, models.Contact.owner_id==user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(c); db.commit()
    return {}
