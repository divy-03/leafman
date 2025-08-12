# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database import get_db
from app.config import settings
from app.models import all_models as m
from app.schemas import token_schemas as ts

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> m.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = ts.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(m.User).filter(m.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: m.User = Depends(get_current_user)) -> m.User:
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user