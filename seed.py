# seed.py
import os
import sys
from getpass import getpass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import date

# This is a bit of a hack to make sure the app modules are found
# when running this script from the project root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models.all_models import User, Base, Department, LeaveType  # Import necessary models
from app.services.auth_service import get_password_hash
from app.services.admin_service import initialize_leave_balances_for_user

def seed_database():
    """
    Creates the first Admin user and essential default data like
    departments and leave types.
    """
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("[-] ERROR: DATABASE_URL environment variable not set.")
        print("[-] Please ensure your .env file is configured or the variable is exported.")
        return

    print(f"[*] Connecting to database...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    print("[+] Connection successful.")

    try:
        # --- Check if Admin already exists ---
        existing_admin = db.query(User).filter(User.role == "Admin").first()
        if existing_admin:
            print(f"[!] Admin user '{existing_admin.email}' already exists. Aborting.")
            return

        print("\n--- Creating First Admin User ---")
        first_name = input("Enter Admin's First Name: ")
        last_name = input("Enter Admin's Last Name: ")
        email = input("Enter Admin's Email: ")
        password = getpass("Enter Admin's Password: ")
        password_confirm = getpass("Confirm Password: ")

        if password != password_confirm:
            print("\n[-] Passwords do not match. Aborting.")
            return

        # --- Create Essential Data (Departments and Leave Types) ---
        print("\n[*] Seeding essential data (Departments, Leave Types)...")
        
        # Departments
        hr_dept = Department(name="HR")
        eng_dept = Department(name="Engineering")
        db.add_all([hr_dept, eng_dept])
        db.flush() # Use flush to get IDs before commit

        # Leave Types
        cl = LeaveType(name="Casual Leave (CL)", annual_quota=12, carry_forward=False)
        el = LeaveType(name="Earned Leave (EL)", annual_quota=15, carry_forward=True)
        db.add_all([cl, el])
        db.commit()
        print("[+] Departments and Leave Types created.")
        
        # --- Create Admin User ---
        print("\n[*] Creating admin user record...")
        hashed_password = get_password_hash(password)
        admin_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hashed_password,
            department_id=hr_dept.department_id,
            join_date=date.today(),
            role="Admin" # Crucial part
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # --- Initialize Admin's Leave Balances ---
        print("[*] Initializing leave balances for admin...")
        initialize_leave_balances_for_user(db, admin_user)

        print("\n[SUCCESS] First Admin user created successfully!")
        print(f"    Name: {admin_user.first_name} {admin_user.last_name}")
        print(f"    Email: {admin_user.email}")
        print("\nYou can now log in using the CLI or API.")

    except Exception as e:
        print(f"\n[-] An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()