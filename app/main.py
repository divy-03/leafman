# app/main.py

from fastapi import FastAPI, Request
import json 

from app.database import engine
from app.models import all_models
from app.routers import auth_router, user_router, leave_router, admin_router

all_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Leave Management System API",
    description="A comprehensive API for managing employee leaves.",
    version="1.0.0"
)

@app.middleware("http")
async def log_headers_middleware(request: Request, call_next):
    # We print this BEFORE the request is processed.
    print(f"[SERVER DEBUG] Request received for: {request.url.path}")
    # Pretty-print the headers
    print(f"[SERVER DEBUG] Incoming Headers: {json.dumps(dict(request.headers), indent=2)}")
    
    response = await call_next(request)
    return response


app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(leave_router.router)
app.include_router(admin_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Leave Management System API"}