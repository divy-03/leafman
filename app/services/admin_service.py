from sqlalchemy.orm import Session
from app.models import all_models as m
from app.schemas import user_schemas as us
from app.services.auth_service import get_password_hash
from decimal import Decimal

def create_user(db: Session, user: us.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = m.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=hashed_password,
        department_id=user.department_id,
        join_date=user.join_date,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    initialize_leave_balances_for_user(db, db_user)

    return db_user

def initialize_leave_balances_for_user(db: Session, user: m.User):
    """
    Creates initial leave balance records for a new user based on their join date.
    """
    current_year = user.join_date.year
    leave_types = db.query(m.LeaveType).all()
    for lt in leave_types:
        # Pro-rate leave based on joining month
        join_month = user.join_date.month
        months_worked = 12 - join_month + 1
        pro_rated_quota = (lt.annual_quota / 12) * months_worked
        
        balance = m.LeaveBalance(
            user_id=user.user_id,
            leave_type_id=lt.leave_type_id,
            year=current_year,
            balance_days=pro_rated_quota,
            used_days=0
        )
        db.add(balance)
    db.commit()