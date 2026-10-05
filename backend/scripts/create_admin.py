"""Create the initial admin account using deployment-provided environment values."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.entities import User


def main():
    username = os.getenv("EDUNEXUS_ADMIN_USERNAME", "").strip()
    email = os.getenv("EDUNEXUS_ADMIN_EMAIL", "").strip()
    password = os.getenv("EDUNEXUS_ADMIN_PASSWORD", "")
    if not username or not email or len(password) < 12:
        raise SystemExit("Set EDUNEXUS_ADMIN_USERNAME, EDUNEXUS_ADMIN_EMAIL, and a password of at least 12 characters.")
    db = SessionLocal()
    try:
        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            if existing.username == username and existing.email == email and existing.role.upper() == "ADMIN":
                print("Admin account already exists; no changes made.")
                return
            raise SystemExit("The requested username or email is already assigned to another account.")
        db.add(User(username=username, email=email, password_hash=hash_password(password), role="ADMIN", is_active=True))
        db.commit()
        print("Admin account created.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
