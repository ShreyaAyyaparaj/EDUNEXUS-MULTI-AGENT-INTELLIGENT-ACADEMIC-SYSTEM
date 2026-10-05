from io import BytesIO
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models.entities import Assessment, Enrollment, Mark, Student, Subject


# ============================================================
# CONSTANTS
# ============================================================

REQUIRED_COLUMNS = {
    "register_number",
    "marks",
}


# ============================================================
# HELPERS
# ============================================================

def _normalize_column_name(column: Any) -> str:
    """
    Normalize uploaded column names so that:
        Register Number
        register_number
        REGISTER NUMBER
    can be interpreted consistently.
    """
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def _normalize_register_number(value: Any) -> str:
    """
    Convert register numbers into a clean string.
    """
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))

    return str(value).strip()


def _read_uploaded_file(
    file_bytes: bytes,
    filename: str,
) -> pd.DataFrame:
    """
    Read CSV or XLSX content into a pandas DataFrame.
    """

    extension = filename.lower().rsplit(".", 1)[-1]

    if extension == "csv":
        return pd.read_csv(BytesIO(file_bytes))

    if extension == "xlsx":
        return pd.read_excel(
            BytesIO(file_bytes),
            engine="openpyxl",
        )

    raise ValueError(
        "Unsupported file format. Please upload a CSV or XLSX file."
    )


def _get_subject_and_assessment(
    db: Session,
    subject_code: str,
    assessment_name: str,
):
    """
    Resolve subject and assessment from PostgreSQL.

    Assessment lookup is case-insensitive.
    """

    normalized_subject_code = subject_code.strip().upper()
    normalized_assessment_name = " ".join(
        assessment_name.strip().split()
    )

    subject = (
        db.query(Subject)
        .filter(
            Subject.code == normalized_subject_code
        )
        .first()
    )

    if subject is None:
        return None, None, "Subject not found."

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.subject_id == subject.id,
            Assessment.name.ilike(normalized_assessment_name),
        )
        .first()
    )

    if assessment is None:
        return (
            subject,
            None,
            "Assessment not found for the selected subject.",
        )

    return subject, assessment, None


def _get_student(
    db: Session,
    register_number: str,
):
    """
    Find a student by register number.
    """

    return (
        db.query(Student)
        .filter(
            Student.register_number == register_number
        )
        .first()
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_marks_upload(
    db: Session,
    file_bytes: bytes,
    filename: str,
    subject_code: str,
    assessment_name: str,
):
    """
    Validate an uploaded CSV/XLSX marks file.

    IMPORTANT:
    This function does NOT modify the database.

    Returns:
        preview
        errors
        warnings
    """

    errors = []
    warnings = []

    # --------------------------------------------------------
    # 1. READ FILE
    # --------------------------------------------------------

    try:
        df = _read_uploaded_file(
            file_bytes=file_bytes,
            filename=filename,
        )
    except Exception as exc:
        return (
            {
                "filename": filename,
                "status": "INVALID_FILE",
                "total_rows": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "duplicate_records": 0,
                "existing_records": 0,
                "records": [],
            },
            [str(exc)],
            [],
        )

    # --------------------------------------------------------
    # 2. NORMALIZE COLUMN NAMES
    # --------------------------------------------------------

    df.columns = [
        _normalize_column_name(column)
        for column in df.columns
    ]

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        errors.append(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

        return (
            {
                "filename": filename,
                "status": "INVALID_SCHEMA",
                "columns": list(df.columns),
                "required_columns": sorted(REQUIRED_COLUMNS),
                "total_rows": len(df),
                "valid_records": 0,
                "invalid_records": len(df),
                "duplicate_records": 0,
                "existing_records": 0,
                "records": [],
            },
            errors,
            warnings,
        )

    # --------------------------------------------------------
    # 3. RESOLVE SUBJECT + ASSESSMENT
    # --------------------------------------------------------

    subject, assessment, lookup_error = _get_subject_and_assessment(
        db,
        subject_code,
        assessment_name,
    )

    if lookup_error:
        errors.append(lookup_error)

        return (
            {
                "filename": filename,
                "status": "REFERENCE_VALIDATION_FAILED",
                "subject_code": subject_code,
                "assessment_name": assessment_name,
                "total_rows": len(df),
                "valid_records": 0,
                "invalid_records": len(df),
                "duplicate_records": 0,
                "existing_records": 0,
                "records": [],
            },
            errors,
            warnings,
        )

    # --------------------------------------------------------
    # 4. PROCESS ROWS
    # --------------------------------------------------------

    records = []

    seen_register_numbers = set()

    valid_records = 0
    invalid_records = 0
    duplicate_records = 0
    existing_records = 0

    for index, row in df.iterrows():

        row_number = index + 2

        register_number = _normalize_register_number(
            row.get("register_number")
        )

        raw_marks = row.get("marks")

        record = {
            "row_number": row_number,
            "register_number": register_number,
            "marks": None,
            "student_id": None,
            "status": "INVALID",
            "reason": None,
        }

        # ----------------------------------------------------
        # Register number
        # ----------------------------------------------------

        if not register_number:
            record["reason"] = "Register number is missing."
            invalid_records += 1
            records.append(record)
            continue

        # ----------------------------------------------------
        # Duplicate inside uploaded file
        # ----------------------------------------------------

        if register_number in seen_register_numbers:
            record["reason"] = (
                "Duplicate register number in uploaded file."
            )
            record["status"] = "DUPLICATE"
            duplicate_records += 1
            records.append(record)
            continue

        seen_register_numbers.add(register_number)

        # ----------------------------------------------------
        # Student lookup
        # ----------------------------------------------------

        student = _get_student(
            db,
            register_number,
        )

        if student is None:
            record["reason"] = "Student not found."
            invalid_records += 1
            records.append(record)
            continue

        record["student_id"] = student.id

        # ----------------------------------------------------
        # Enrollment validation
        # ----------------------------------------------------

        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.student_id == student.id,
                Enrollment.subject_id == subject.id,
            )
            .first()
        )

        if enrollment is None:
            record["reason"] = (
                "Student is not enrolled in this subject."
            )
            invalid_records += 1
            records.append(record)
            continue

        # ----------------------------------------------------
        # Marks validation
        # ----------------------------------------------------

        if pd.isna(raw_marks):
            record["reason"] = "Marks are missing."
            invalid_records += 1
            records.append(record)
            continue

        try:
            marks = float(raw_marks)
        except (TypeError, ValueError):
            record["reason"] = "Marks must be numeric."
            invalid_records += 1
            records.append(record)
            continue

        record["marks"] = marks

        if marks < 0:
            record["reason"] = "Marks cannot be negative."
            invalid_records += 1
            records.append(record)
            continue

        if marks > float(assessment.max_marks):
            record["reason"] = (
                f"Marks cannot exceed "
                f"{float(assessment.max_marks)}."
            )
            invalid_records += 1
            records.append(record)
            continue

        # ----------------------------------------------------
        # Existing mark validation
        # ----------------------------------------------------

        existing_mark = (
            db.query(Mark)
            .filter(
                Mark.student_id == student.id,
                Mark.assessment_id == assessment.id,
            )
            .first()
        )

        if existing_mark is not None:
            record["status"] = "EXISTING"
            record["existing_marks"] = float(
                existing_mark.marks_obtained
            )
            record["reason"] = (
                "A mark already exists for this assessment."
            )

            existing_records += 1
            records.append(record)
            continue

        # ----------------------------------------------------
        # VALID
        # ----------------------------------------------------

        record["status"] = "VALID"
        valid_records += 1

        records.append(record)

    # --------------------------------------------------------
    # 5. WARNINGS
    # --------------------------------------------------------

    if existing_records > 0:
        warnings.append(
            f"{existing_records} record(s) already have marks "
            "for this assessment. They will not be overwritten."
        )

    if duplicate_records > 0:
        warnings.append(
            f"{duplicate_records} duplicate register number(s) "
            "were found in the uploaded file."
        )

    if valid_records == 0:
        warnings.append(
            "No new valid marks are available for import."
        )

    # --------------------------------------------------------
    # 6. FINAL STATUS
    # --------------------------------------------------------

    if valid_records > 0:
        status = "READY_FOR_CONFIRMATION"
    else:
        status = "VALIDATION_FAILED"

    preview = {
        "filename": filename,
        "subject_code": subject.code,
        "subject_name": subject.name,
        "assessment_name": assessment.name,
        "assessment_type": assessment.assessment_type,
        "max_marks": float(assessment.max_marks),
        "total_rows": len(df),
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_records,
        "existing_records": existing_records,
        "records": records,
        "status": status,
    }

    return preview, errors, warnings

# ============================================================
# COMMIT MARKS UPLOAD
# ============================================================

def commit_marks_upload(
    db: Session,
    file_bytes: bytes,
    filename: str,
    subject_code: str,
    assessment_name: str,
    faculty,
):
    """
    Revalidate and commit a CSV/XLSX marks upload.

    Only records with status == VALID are inserted.

    Existing marks are never overwritten by this workflow.

    The complete operation is performed as one transaction.
    """

    # --------------------------------------------------------
    # 1. Revalidate immediately before database write
    # --------------------------------------------------------

    preview, errors, warnings = validate_marks_upload(
        db=db,
        file_bytes=file_bytes,
        filename=filename,
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

    valid_records = [
        record
        for record in preview["records"]
        if record["status"] == "VALID"
    ]

    if not valid_records:
        return {
            "status": "VALIDATION_FAILED",
            "errors": [],
            "warnings": warnings + [
                "No new valid marks are available for import."
            ],
            "preview": preview,
        }

    # --------------------------------------------------------
    # 2. Resolve subject + assessment again
    # --------------------------------------------------------

    subject, assessment, lookup_error = _get_subject_and_assessment(
        db,
        subject_code,
        assessment_name,
    )

    if lookup_error:
        return {
            "status": "VALIDATION_FAILED",
            "errors": [lookup_error],
            "warnings": warnings,
            "preview": preview,
        }

    # --------------------------------------------------------
    # 3. Transaction
    # --------------------------------------------------------

    try:
        committed_records = []

        for record in valid_records:

            # ------------------------------------------------
            # Re-check student
            # ------------------------------------------------

            student = (
                db.query(Student)
                .filter(
                    Student.id == record["student_id"],
                    Student.register_number
                    == record["register_number"],
                )
                .first()
            )

            if student is None:
                raise RuntimeError(
                    "A student changed between validation and "
                    "confirmation. Please validate the file again."
                )

            # ------------------------------------------------
            # Re-check existing mark
            # ------------------------------------------------

            existing_mark = (
                db.query(Mark)
                .filter(
                    Mark.student_id == student.id,
                    Mark.assessment_id == assessment.id,
                )
                .first()
            )

            if existing_mark is not None:
                raise RuntimeError(
                    f"A mark already exists for "
                    f"{record['register_number']}. "
                    "Please validate the file again."
                )

            # ------------------------------------------------
            # Insert mark
            # ------------------------------------------------

            mark = Mark(
                student_id=student.id,
                assessment_id=assessment.id,
                marks_obtained=record["marks"],
            )

            db.add(mark)

            committed_records.append({
                "register_number": record["register_number"],
                "marks": float(record["marks"]),
            })

        # ----------------------------------------------------
        # 4. Audit log
        # ----------------------------------------------------

        from datetime import datetime, timezone
        import json

        from app.models.entities import AuditLog

        audit_log = AuditLog(
            user_id=faculty.user_id,
            action="MARKS_BULK_UPLOADED",
            entity_type="ASSESSMENT",
            entity_id=str(assessment.id),
            details=json.dumps({
                "filename": filename,
                "subject_code": subject.code,
                "subject_name": subject.name,
                "assessment_name": assessment.name,
                "assessment_type": assessment.assessment_type,
                "max_marks": float(assessment.max_marks),
                "total_rows": preview["total_rows"],
                "committed_records": len(committed_records),
                "invalid_records": preview["invalid_records"],
                "duplicate_records": preview["duplicate_records"],
                "existing_records": preview["existing_records"],
                "records": committed_records,
            }),
            created_at=datetime.now(timezone.utc),
        )

        db.add(audit_log)

        # ----------------------------------------------------
        # 5. Commit
        # ----------------------------------------------------

        db.commit()

        return {
            "status": "COMMITTED",
            "message": "Marks uploaded successfully",
            "assessment_id": assessment.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "assessment_name": assessment.name,
            "committed_records": len(committed_records),
            "invalid_records": preview["invalid_records"],
            "duplicate_records": preview["duplicate_records"],
            "existing_records": preview["existing_records"],
            "records": committed_records,
            "warnings": warnings,
        }

    except Exception as exc:
        db.rollback()

        raise RuntimeError(
            f"Marks bulk upload failed: {exc}"
        )