# app/routers/admin_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app import database, models
from app.dependencies import get_current_admin_user
from app.schemas import user_schemas, leave_schemas
from app.services import admin_service, leave_service
from app.schemas.leave_schemas import DepartmentCreate, DepartmentResponse, LeaveTypeCreate, LeaveTypeResponse

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)]
)

@router.post("/users", response_model=user_schemas.UserResponse, status_code=201)
def add_new_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    # Logic to create user and initialize balances
    return admin_service.create_user(db=db, user=user)

@router.get("/leave-requests", response_model=List[leave_schemas.LeaveRequestResponse])
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

@router.patch("/leave-requests/{request_id}", response_model=leave_schemas.LeaveRequestResponse)
def update_leave_request_status(
    request_id: int,
    approval: leave_schemas.LeaveApproval,
    db: Session = Depends(database.get_db),
    admin_user: models.all_models.User = Depends(get_current_admin_user)
):
    return leave_service.process_leave_request(db, request_id, approval, admin_user)

@router.post("/leave-types", response_model=LeaveTypeResponse, status_code=201)
def create_leave_type(
    leave_type: LeaveTypeCreate,
    db: Session = Depends(database.get_db)
):
    db_leave_type = models.all_models.LeaveType(**leave_type.model_dump())
    db.add(db_leave_type)
    db.commit()
    db.refresh(db_leave_type)
    return db_leave_type

@router.post("/departments", response_model=DepartmentResponse, status_code=201)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(database.get_db)
):
    db_department = models.all_models.Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department