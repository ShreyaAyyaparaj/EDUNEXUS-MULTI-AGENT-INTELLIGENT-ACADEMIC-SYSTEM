from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AttendanceParseRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        description="Natural-language attendance instruction from faculty"
    )


class AttendanceParseResult(BaseModel):
    subject_code: Optional[str] = None
    date: Optional[date] = None
    period: Optional[int] = Field(default=None, ge=1, le=10)
    section: Optional[str] = None
    absent_student_ids: list[str] = []

    @field_validator("subject_code", "section")
    @classmethod
    def normalize_optional_text(cls, value):
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("absent_student_ids")
    @classmethod
    def validate_student_ids(cls, value):
        cleaned = [
            student_id.strip()
            for student_id in value
            if student_id.strip()
        ]

        if len(cleaned) != len(set(cleaned)):
            raise ValueError(
                "Duplicate student register numbers are not allowed"
            )

        return cleaned


class AttendanceRequest(BaseModel):
    """
    Fully validated attendance request.
    Used after the AI parsing stage.
    """

    subject_code: str
    date: date
    period: int = Field(..., ge=1, le=10)
    section: str
    absent_student_ids: list[str]

    @field_validator("subject_code", "section")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("absent_student_ids")
    @classmethod
    def validate_student_ids(cls, value):
        cleaned = [
            student_id.strip()
            for student_id in value
            if student_id.strip()
        ]

        if len(cleaned) != len(set(cleaned)):
            raise ValueError(
                "Duplicate student register numbers are not allowed"
            )

        return cleaned


class AttendanceValidationRequest(BaseModel):
    attendance: AttendanceRequest


class AttendanceConfirmRequest(BaseModel):
    attendance: AttendanceRequest


class AttendancePreview(BaseModel):
    subject_code: str
    subject_name: str
    date: date
    period: int
    semester: int
    section: str

    total_students: int
    present_count: int
    absent_count: int

    absent_student_ids: list[str]
    present_student_ids: list[str]

    warnings: list[str] = []
    status: str
