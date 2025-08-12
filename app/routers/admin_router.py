# app/routers/admin_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app import database, dependencies, models, schemas
from app.services import admin_service, leave_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(dependencies.get_current_admin_user)]
)

@router.post("/users", response_model=schemas.user_schemas.UserResponse, status_code=201)
def add_new_user(
    user: schemas.user_schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    # Logic to create user and initialize balances
    return admin_service.create_user(db=db, user=user)

@router.get("/leave-requests", response_model=List[schemas.leave_schemas.LeaveRequestResponse])
def list_all_leave_requests(
    db: Session = Depends(database.get_db),
    status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100)
):
    query = db.query(models.all_models.LeaveRequest)
    if status:
        query = query.filter(models.all_models.LeaveRequest.status == status)
    
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

@router.patch("/leave-requests/{request_id}", response_model=schemas.leave_schemas.LeaveRequestResponse)
def update_leave_request_status(
    request_id: int,
    approval: schemas.leave_schemas.LeaveApproval,
    db: Session = Depends(database.get_db),
    admin_user: models.all_models.User = Depends(dependencies.get_current_admin__user)
):
    return leave_service.process_leave_request(db, request_id, approval, admin_user)