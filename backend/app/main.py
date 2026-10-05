from app.api import copilot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.student import router as student_router
from app.api.faculty import router as faculty_router
from app.api.workflows import router as workflows_router


app = FastAPI(
    title="EduNexus API",
    description="Agentic Academic Operating System",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(student_router)
app.include_router(faculty_router)
app.include_router(workflows_router)


@app.get("/", tags=["System"])
def root():
    return {
        "application": "EduNexus",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}

app.include_router(copilot.router)

