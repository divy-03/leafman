# app/schemas/leave_schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .user_schemas import UserInLeaveRequestResponse

# Schemas for LeaveType
class LeaveTypeBase(BaseModel):
    name: str
    paid: bool = True
    annual_quota: Decimal
    carry_forward: bool = False

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeResponse(LeaveTypeBase):
    leave_type_id: int

    class Config:
        from_attributes = True

# Schemas for LeaveRequest
class LeaveRequestCreate(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    is_half_day: bool = False
    reason: Optional[str] = None

class LeaveRequestResponse(BaseModel):
    request_id: int
    user_id: int
    leave_type: LeaveTypeResponse
    start_date: date
    end_date: date
    total_days: Decimal
    is_half_day: bool
    status: str
    reason: Optional[str] = None

    class Config:
        from_attributes = True

# Schemas for LeaveBalance
class LeaveBalanceResponse(BaseModel):
    leave_type: LeaveTypeResponse
    year: int
    balance_days: Decimal
    used_days: Decimal
    
    class Config:
        from_attributes = True

# Schema for Admin actions
class LeaveApproval(BaseModel):
    status: str # "Approved" or "Rejected"
    approval_note: Optional[str] = None

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    department_id: int
    class Config:
        from_attributes = True

class AdminLeaveRequestResponse(BaseModel):
    request_id: int
    user: UserInLeaveRequestResponse 
    leave_type: LeaveTypeResponse
    start_date: date
    end_date: date
    total_days: Decimal
    status: str
    reason: Optional[str] = None

    class Config:
        from_attributes = True