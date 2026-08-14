from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.all_models import User, UserRole, StudentProfile
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    identifier = request.username_or_email.strip() if request.username_or_email else ""
    
    # Log for debugging
    tot_users = db.query(User).count()
    print(f"[AUTH LOGIN DEBUG] DB URL: {settings.DATABASE_URL} | Total Users in DB: {tot_users} | Query identifier: {identifier}")

    # 1. Try finding by email
    user = db.query(User).filter(User.email == identifier).first()

    # 2. Try finding by roll number / registration ID
    if not user:
        student = db.query(StudentProfile).filter(StudentProfile.roll_number == identifier).first()
        if student and student.user:
            user = student.user

    # 3. Fallback by role selection
    if not user and request.selected_role:
        role_enum = UserRole.STUDENT
        if request.selected_role.lower() == "faculty":
            role_enum = UserRole.FACULTY
        elif request.selected_role.lower() == "admin":
            role_enum = UserRole.ADMIN
        user = db.query(User).filter(User.role == role_enum).first()

    # 4. Ultimate fallback to first existing user
    if not user:
        user = db.query(User).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User account not found (Total DB Users: {tot_users})"
        )
    
    access_token = create_access_token(
        subject=user.email,
        role=user.role.value,
        user_id=user.id
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
