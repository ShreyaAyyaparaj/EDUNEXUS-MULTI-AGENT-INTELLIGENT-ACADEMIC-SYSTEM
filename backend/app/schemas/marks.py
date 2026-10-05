from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MarksParseRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        description="Natural-language description of the marks file"
    )


class ParsedMark(BaseModel):
    register_number: str
    marks: float

    @field_validator("register_number")
    @classmethod
    def normalize_register_number(cls, value: str) -> str:
        return value.strip()


class MarksParseResult(BaseModel):
    assessment_name: Optional[str] = None
    assessment_type: Optional[str] = None
    subject_code: Optional[str] = None
    max_marks: Optional[float] = None
    records: list[ParsedMark] = []

    @field_validator("subject_code", "assessment_type")
    @classmethod
    def normalize_optional_text(cls, value):
        if value is None:
            return None
        return value.strip().upper()


class MarksRequest(BaseModel):
    subject_code: str
    assessment_name: str
    marks: dict[str, float]

    @field_validator("subject_code", "assessment_name")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip().upper()


class MarksValidationRequest(BaseModel):
    marks: MarksRequest


class MarksConfirmRequest(BaseModel):
    marks: MarksRequest


class MarksPreview(BaseModel):
    subject_code: str
    subject_name: str
    assessment_name: str
    assessment_type: str
    max_marks: float

    total_records: int
    valid_records: int
    invalid_records: int

    records: list[dict]
    errors: list[str] = []
    warnings: list[str] = []

    status: str
