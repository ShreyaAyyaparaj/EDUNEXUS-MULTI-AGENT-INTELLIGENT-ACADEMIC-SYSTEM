import os
import sys
# Include root workspace directory in python path for agents import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import engine, Base
from app.routers import auth, student, faculty, admin, agent
from app.scheduler.jobs import start_scheduler

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware for React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler to guarantee zero unhandled 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. EduNexus fallback system has handled this gracefully.",
            "error_type": type(exc).__name__,
            "message": str(exc)
        }
    )

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(student.router, prefix=settings.API_V1_STR)
app.include_router(faculty.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    try:
        start_scheduler()
    except Exception as e:
        print(f"Scheduler startup warning: {e}")

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "docs": "/docs"
    }
