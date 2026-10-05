from fastapi import APIRouter, Depends, HTTPException, File,Form,UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_faculty
from app.db.database import get_db
from app.models.entities import User
from app.services.marks_upload_service import (
    validate_marks_upload,
    commit_marks_upload,
)
from app.schemas.attendance import (
    AttendanceParseRequest,
    AttendanceParseResult,
    AttendanceValidationRequest,
    AttendanceConfirmRequest,
)

from app.schemas.marks import (
    MarksParseRequest,
    MarksParseResult,
    MarksValidationRequest,
    MarksConfirmRequest,
)

from app.services.attendance_service import (
    get_faculty as get_attendance_faculty,
    validate_attendance,
    commit_attendance,
)

from app.services.marks_service import (
    get_faculty as get_marks_faculty,
    validate_marks,
    commit_marks,
    validate_mark_updates,
    commit_mark_updates,
)

from app.services.gemini_service import gemini_service


router = APIRouter(
    prefix="/api/faculty",
    tags=["Faculty"],
)


# ============================================================
# SMART ATTENDANCE
# ============================================================

@router.post("/attendance/parse")
def parse_attendance(
    request: AttendanceParseRequest,
    current_user: User = Depends(require_faculty),
):
    """
    Stage 1:
    Gemini interprets natural-language attendance instructions.

    Gemini does not modify the database.
    """

    parsed = gemini_service.parse_attendance(request.text)

    try:
        result = AttendanceParseResult.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid Gemini attendance output: {exc}",
        )

    return {
        "status": "PARSED",
        "source": "gemini",
        "attendance": result.model_dump(),
    }


@router.post("/attendance/validate")
def validate_attendance_request(
    request: AttendanceValidationRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Stage 2:
    Deterministic validation against PostgreSQL.

    No database write occurs here.
    """

    faculty = get_attendance_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    preview, _, errors, warnings = validate_attendance(
        db,
        faculty,
        request.attendance,
    )

    if errors:
        return {
            "status": "VALIDATION_FAILED",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
        }

    return {
        "status": "READY_FOR_CONFIRMATION",
        "errors": [],
        "warnings": warnings,
        "preview": preview,
    }


@router.post("/attendance/confirm")
def confirm_attendance(
    request: AttendanceConfirmRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Stage 3:
    Revalidate and commit attendance.
    """

    faculty = get_attendance_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    return commit_attendance(
        db,
        faculty,
        request.attendance,
    )


# ============================================================
# SMART MARKS — ADD
# ============================================================

@router.post("/marks/parse")
def parse_marks(
    request: MarksParseRequest,
    current_user: User = Depends(require_faculty),
):
    """
    Stage 1:
    Gemini interprets a faculty's description of marks data.

    This endpoint does NOT modify PostgreSQL.
    """

    parsed = gemini_service.parse_marks(request.text)

    try:
        result = MarksParseResult.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid Gemini marks output: {exc}",
        )

    return {
        "status": "PARSED",
        "source": "gemini",
        "marks": result.model_dump(),
    }


@router.post("/marks/validate")
def validate_marks_request(
    request: MarksValidationRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Stage 2:
    Deterministic marks validation.

    Existing marks are rejected here.
    Use /marks/update/validate for explicit updates.
    """

    faculty = get_marks_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    data = request.marks

    preview, errors, warnings = validate_marks(
        db,
        faculty,
        data.subject_code,
        data.assessment_name,
        data.marks,
    )

    if errors:
        return {
            "status": "VALIDATION_FAILED",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
        }

    return {
        "status": "READY_FOR_CONFIRMATION",
        "errors": [],
        "warnings": warnings,
        "preview": preview,
    }


@router.post("/marks/confirm")
def confirm_marks(
    request: MarksConfirmRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Stage 3:
    Revalidate and commit NEW marks.
    """

    faculty = get_marks_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    data = request.marks

    return commit_marks(
        db,
        faculty,
        data.subject_code,
        data.assessment_name,
        data.marks,
    )


# ============================================================
# SMART MARKS — UPDATE EXISTING
# ============================================================

@router.post("/marks/update/validate")
def validate_mark_updates_request(
    request: MarksValidationRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Stage 1:
    Validate an explicit request to UPDATE existing marks.

    No database write occurs here.

    Existing marks are required.
    Missing marks are rejected.
    """

    faculty = get_marks_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    data = request.marks

    preview, errors, warnings = validate_mark_updates(
        db,
        faculty,
        data.subject_code,
        data.assessment_name,
        data.marks,
    )

    if errors:
        return {
            "status": "VALIDATION_FAILED",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
        }

    return {
        "status": "READY_FOR_CONFIRMATION",
        "errors": [],
        "warnings": warnings,
        "preview": preview,
    }


@router.post("/marks/update/confirm")
def confirm_mark_updates(
    request: MarksConfirmRequest,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Stage 2:
    Revalidate and UPDATE existing marks.

    The operation is transactional and creates an
    MARKS_UPDATED audit log.
    """

    faculty = get_marks_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    data = request.marks

    return commit_mark_updates(
        db,
        faculty,
        data.subject_code,
        data.assessment_name,
        data.marks,
    )
# ============================================================
# BULK MARKS UPLOAD — VALIDATE
# ============================================================

@router.post("/marks/upload/validate")

def validate_marks_upload_request(
    file: UploadFile = File(...),
    subject_code: str = Form(...),
    assessment_name: str = Form(...),
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Validate a CSV/XLSX marks upload.

    No database write occurs here.

    The uploaded file is parsed and validated against:
    - Subject
    - Assessment
    - Student register numbers
    - Enrollment
    - Mark range
    - Duplicate rows
    - Existing marks
    """

    # --------------------------------------------------------
    # Faculty validation
    # --------------------------------------------------------

    faculty = get_marks_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    # --------------------------------------------------------
    # File validation
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required.",
        )

    filename = file.filename.lower()

    if not (
        filename.endswith(".csv")
        or filename.endswith(".xlsx")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported.",
        )

    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    file_bytes = file.file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    preview, errors, warnings = validate_marks_upload(
        db=db,
        file_bytes=file_bytes,
        filename=file.filename,
        subject_code=subject_code,
        assessment_name=assessment_name,
    )

    if errors:
        return {
            "status": "VALIDATION_FAILED",
            "errors": errors,
            "warnings": warnings,
            "preview": preview,
        }

    return {
        "status": preview["status"],
        "errors": [],
        "warnings": warnings,
        "preview": preview,
    }
# ============================================================
# BULK MARKS UPLOAD — CONFIRM
# ============================================================

@router.post("/marks/upload/confirm")
def confirm_marks_upload(
    file: UploadFile = File(...),
    subject_code: str = Form(...),
    assessment_name: str = Form(...),
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    """
    Revalidate and commit a CSV/XLSX marks upload.

    Only new valid marks are inserted.
    Existing marks are never overwritten.
    """

    # --------------------------------------------------------
    # Faculty validation
    # --------------------------------------------------------

    faculty = get_marks_faculty(
        db,
        current_user.id,
    )

    if faculty is None:
        raise HTTPException(
            status_code=404,
            detail="Faculty profile not found",
        )

    # --------------------------------------------------------
    # File validation
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required.",
        )

    filename = file.filename.lower()

    if not (
        filename.endswith(".csv")
        or filename.endswith(".xlsx")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported.",
        )

    file_bytes = file.file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # --------------------------------------------------------
    # Revalidate + commit
    # --------------------------------------------------------

    return commit_marks_upload(
        db=db,
        file_bytes=file_bytes,
        filename=file.filename,
        subject_code=subject_code,
        assessment_name=assessment_name,
        faculty=faculty,
    )