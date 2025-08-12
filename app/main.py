# app/main.py
from fastapi import FastAPI
from app.database import engine
from app.models import all_models
from app.routers import auth_router, user_router, leave_router, admin_router

# Create all database tables (on startup)
all_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Leave Management System API",
    description="A comprehensive API for managing employee leaves.",
    version="1.0.0"
)

# Include all the routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(leave_router.router)
app.include_router(admin_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Leave Management System API"}