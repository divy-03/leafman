# app/routers/leave_router.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app import database, dependencies, models, schemas
from app.services import leave_service

router = APIRouter(
    prefix="/leave-requests",
    tags=["Leave Requests"]
)

@router.get("/types", response_model=List[schemas.leave_schemas.LeaveTypeResponse])
def get_all_leave_types(db: Session = Depends(database.get_db)):
    return db.query(models.all_models.LeaveType).all()

@router.post("/", response_model=schemas.leave_schemas.LeaveRequestResponse, status_code=201)
def create_leave_request(
    request: schemas.leave_schemas.LeaveRequestCreate,
    db: Session = Depends(database.get_db),
    current_user: models.all_models.User = Depends(dependencies.get_current_user)
):
    return leave_service.apply_for_leave(db=db, user=current_user, request=request)

@router.get("/", response_model=List[schemas.leave_schemas.LeaveRequestResponse])
def get_my_leave_requests(
    db: Session = Depends(database.get_db),
    current_user: models.all_models.User = Depends(dependencies.get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100)
):
    offset = (page - 1) * limit
    return db.query(models.all_models.LeaveRequest).filter(
        models.all_models.LeaveRequest.user_id == current_user.user_id
    ).offset(offset).limit(limit).all()