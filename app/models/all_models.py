# app/models/all_models.py
from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Boolean,
    ForeignKey, TIMESTAMP, TEXT, DECIMAL, CHAR
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(TEXT, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.department_id'), nullable=True)
    join_date = Column(Date)
    role = Column(String(10), default='Employee', nullable=False)  # 'Employee' or 'Admin'
    country_code = Column(CHAR(2))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    department = relationship("Department")
    leave_requests = relationship("LeaveRequest", back_populates="user")
    leave_balances = relationship("LeaveBalance", back_populates="user")

class Department(Base):
    __tablename__ = 'departments'
    department_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class LeaveType(Base):
    __tablename__ = 'leave_types'
    leave_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    paid = Column(Boolean, default=True)
    annual_quota = Column(DECIMAL(5, 2), nullable=False)
    carry_forward = Column(Boolean, default=False)
    country_code = Column(CHAR(2))

class LeaveBalance(Base):
    __tablename__ = 'leave_balances'
    balance_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    leave_type_id = Column(Integer, ForeignKey('leave_types.leave_type_id'), nullable=False)
    year = Column(Integer, nullable=False)
    balance_days = Column(DECIMAL(5, 2), nullable=False)
    used_days = Column(DECIMAL(5, 2), default=0)

    user = relationship("User", back_populates="leave_balances")
    leave_type = relationship("LeaveType")

class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    leave_type_id = Column(Integer, ForeignKey('leave_types.leave_type_id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(DECIMAL(5, 2), nullable=False)
    is_half_day = Column(Boolean, default=False)
    reason = Column(TEXT)
    status = Column(String(20), default='Pending', nullable=False)
    applied_at = Column(TIMESTAMP, server_default=func.now())
    approved_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    approval_note = Column(TEXT)
    
    user = relationship("User", back_populates="leave_requests")
    leave_type = relationship("LeaveType")
    approver = relationship("User", foreign_keys=[approved_by])

class Holiday(Base):
    __tablename__ = 'holidays'
    holiday_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    holiday_date = Column(Date, unique=True, nullable=False)
    country_code = Column(CHAR(2))