"""Add mentor requests and achievement review fields.

Revision ID: 20260929_01
Revises: e980026286a1
"""
from alembic import op
import sqlalchemy as sa

revision = "20260929_01"
down_revision = "e980026286a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("achievements", sa.Column("achievement_date", sa.Date(), nullable=True))
    op.add_column("achievements", sa.Column("certificate_name", sa.String(255), nullable=True))
    op.add_column("achievements", sa.Column("certificate_path", sa.String(500), nullable=True))
    op.add_column("achievements", sa.Column("faculty_message", sa.Text(), nullable=True))
    op.add_column("achievements", sa.Column("reviewed_by", sa.Integer(), nullable=True))
    op.add_column("achievements", sa.Column("reviewed_at", sa.DateTime(), nullable=True))
    op.create_foreign_key("fk_achievements_reviewed_by_faculty", "achievements", "faculty", ["reviewed_by"], ["id"])
    op.create_table(
        "mentor_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("faculty_id", sa.Integer(), sa.ForeignKey("faculty.id"), nullable=False),
        sa.Column("project_domain", sa.String(200), nullable=False),
        sa.Column("query", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("faculty_message", sa.Text(), nullable=True),
        sa.Column("email_status", sa.String(30), nullable=False, server_default="NOT_CONFIGURED"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_mentor_requests_student_id", "mentor_requests", ["student_id"])
    op.create_index("ix_mentor_requests_faculty_id", "mentor_requests", ["faculty_id"])
    op.create_index("ix_mentor_requests_status", "mentor_requests", ["status"])


def downgrade() -> None:
    op.drop_table("mentor_requests")
    op.drop_constraint("fk_achievements_reviewed_by_faculty", "achievements", type_="foreignkey")
    for column in ("reviewed_at", "reviewed_by", "faculty_message", "certificate_path", "certificate_name", "achievement_date"):
        op.drop_column("achievements", column)
