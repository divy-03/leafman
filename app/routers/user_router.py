# app/routers/user_router.py
from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime

from app import dependencies, schemas
from app.database import get_db
from app.services import leave_service
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(dependencies.get_current_user)]
)

@router.get("/me", response_model=schemas.user_schemas.UserResponse)
def read_users_me(current_user: schemas.user_schemas.UserResponse = Depends(dependencies.get_current_user)):
    return current_user

@router.get("/me/balances", response_model=List[schemas.leave_schemas.LeaveBalanceResponse])
def get_my_leave_balances(
    db: Session = Depends(get_db),
    current_user: schemas.user_schemas.UserResponse = Depends(dependencies.get_current_user)
):
    current_year = datetime.now().year
    return leave_service.get_leave_balances(db, user_id=current_user.user_id, year=current_year)