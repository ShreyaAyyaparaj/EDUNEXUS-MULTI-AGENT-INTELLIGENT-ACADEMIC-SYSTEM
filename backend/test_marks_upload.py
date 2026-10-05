from app.db.database import SessionLocal
from app.services.marks_upload_service import validate_marks_upload


# ============================================================
# TEST DATA
# ============================================================

CSV_CONTENT = """register_number,marks
2116231401103,90
2116231401104,78
2116231401105,85
2116231401103,95
INVALID_REGISTER,80
2116231401106,150
2116231401107,
"""


# ============================================================
# RUN TEST
# ============================================================

def main():
    db = SessionLocal()

    try:
        preview, errors, warnings = validate_marks_upload(
            db=db,
            file_bytes=CSV_CONTENT.encode("utf-8"),
            filename="test_marks.csv",
            subject_code="CB23721",
            assessment_name="Project Evaluation I",
        )

        print("\n" + "=" * 70)
        print("MARKS UPLOAD VALIDATION TEST")
        print("=" * 70)

        print("\nERRORS:")
        for error in errors:
            print(f"  - {error}")

        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

        print("\nPREVIEW:")
        print(f"  Filename          : {preview.get('filename')}")
        print(f"  Subject           : {preview.get('subject_code')} - "
              f"{preview.get('subject_name')}")
        print(f"  Assessment        : {preview.get('assessment_name')}")
        print(f"  Max Marks         : {preview.get('max_marks')}")
        print(f"  Total Rows        : {preview.get('total_rows')}")
        print(f"  Valid Records     : {preview.get('valid_records')}")
        print(f"  Invalid Records   : {preview.get('invalid_records')}")
        print(f"  Duplicate Records : {preview.get('duplicate_records')}")
        print(f"  Existing Records  : {preview.get('existing_records')}")
        print(f"  Status            : {preview.get('status')}")

        print("\nRECORD DETAILS:")
        print("-" * 70)

        for record in preview.get("records", []):
            print(
                f"Row {record['row_number']:>2} | "
                f"{record['register_number']:<18} | "
                f"Marks: {str(record['marks']):<6} | "
                f"Status: {record['status']:<10} | "
                f"Reason: {record['reason']}"
            )

        print("\n" + "=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    main()