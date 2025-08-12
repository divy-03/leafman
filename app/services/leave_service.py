# app/services/leave_service.py
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta
from app.models import all_models as m
from app.schemas import leave_schemas as ls
from fastapi import HTTPException, status
from decimal import Decimal

def get_leave_balances(db: Session, user_id: int, year: int):
    return db.query(m.LeaveBalance).options(joinedload(m.LeaveBalance.leave_type)).filter(
        m.LeaveBalance.user_id == user_id,
        m.LeaveBalance.year == year
    ).all()

def apply_for_leave(db: Session, user: m.User, request: ls.LeaveRequestCreate):
    # 1. Basic Validations
    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date.")
    if request.start_date < user.join_date:
        raise HTTPException(status_code=400, detail="Cannot apply for leave before joining date.")

    # 2. Check for overlapping requests
    overlapping = db.query(m.LeaveRequest).filter(
        m.LeaveRequest.user_id == user.user_id,
        m.LeaveRequest.status.in_(['Pending', 'Approved']),
        m.LeaveRequest.start_date <= request.end_date,
        m.LeaveRequest.end_date >= request.start_date
    ).first()
    if overlapping:
        raise HTTPException(status_code=400, detail="Overlapping leave request already exists.")

    # 3. Calculate total leave days
    # This is a simple calculation; a real one would exclude weekends/holidays
    # For simplicity in this MVP, we use date difference.
    if request.is_half_day:
        total_days = Decimal("0.5")
        if request.start_date != request.end_date:
            raise HTTPException(status_code=400, detail="Half-day leave must be for a single day.")
    else:
        total_days = (request.end_date - request.start_date).days + 1

    # 4. Check sufficient balance
    balance = db.query(m.LeaveBalance).filter(
        m.LeaveBalance.user_id == user.user_id,
        m.LeaveBalance.leave_type_id == request.leave_type_id,
        m.LeaveBalance.year == request.start_date.year
    ).first()

    if not balance or (balance.balance_days - balance.used_days) < total_days:
        raise HTTPException(status_code=400, detail="Insufficient leave balance.")

    # 5. Create Leave Request
    db_request = m.LeaveRequest(
        user_id=user.user_id,
        leave_type_id=request.leave_type_id,
        start_date=request.start_date,
        end_date=request.end_date,
        is_half_day=request.is_half_day,
        total_days=total_days,
        reason=request.reason,
        status='Pending'
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def process_leave_request(db: Session, request_id: int, approval_data: ls.LeaveApproval, approver: m.User):
    db_request = db.query(m.LeaveRequest).filter(m.LeaveRequest.request_id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    if db_request.status != 'Pending':
        raise HTTPException(status_code=400, detail="Leave request has already been processed.")

    db_request.status = approval_data.status
    db_request.approved_by = approver.user_id
    db_request.approval_note = approval_data.approval_note
    
    # If approved, deduct from balance
    if approval_data.status == 'Approved':
        balance = db.query(m.LeaveBalance).filter(
            m.LeaveBalance.user_id == db_request.user_id,
            m.LeaveBalance.leave_type_id == db_request.leave_type_id,
            m.LeaveBalance.year == db_request.start_date.year
        ).first()
        if not balance:
            raise HTTPException(status_code=400, detail="Leave balance record not found for user.")
        
        balance.used_days += db_request.total_days

    db.commit()
    db.refresh(db_request)
    return db_request