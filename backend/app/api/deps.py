#get current user dependency
#db dependency in db/session.py

from sqlalchemy.orm import Session # type: ignore
from fastapi import Depends, HTTPException,status # type: ignore
from ..db.session import get_db
from ..core.security import token_decode
from ..models.user import Student
from fastapi.security import OAuth2PasswordBearer # type: ignore
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "/login")

def get_current_user(token: str = Depends(oauth2_scheme), db:Session=Depends(get_db)):
    payload = token_decode(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(Student).filter(Student.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

