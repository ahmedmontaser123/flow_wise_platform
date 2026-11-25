"""HR RBAC (role, status, approval) and job titles catalog

Revision ID: c3f1a9e7b2d4
Revises: aa7da30d5100
Create Date: 2026-11-16 00:00:00

What this migration does
------------------------
hr_users
  + role            hr_role enum (ADMIN / MEMBER), default MEMBER
  + status          hr_account_status enum, default PENDING
                    (rows that already exist are set to ACTIVE so nobody is locked out)
  + approved_by_id  FK -> hr_users.id (ON DELETE SET NULL)
  + approved_at     timestamptz
  + token_version   int, bumped to invalidate old JWTs (password change, disable, ...)
  + partial unique index: only ONE admin per company

job_titles (new table)
  company-scoped catalog, name unique per company (case-insensitive)

jobs
  + job_title_id    FK -> job_titles.id (ON DELETE RESTRICT), nullable
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c3f1a9e7b2d4"
down_revision: Union[str, None] = "aa7da30d5100"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# SQLAlchemy stores Python enums by member NAME, so the DB labels are upper case.
hr_role = postgresql.ENUM("ADMIN", "MEMBER", name="hr_role", create_type=False)
hr_account_status = postgresql.ENUM(
    "PENDING", "ACTIVE", "DECLINED", "DISABLED",
    name="hr_account_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    hr_role.create(bind, checkfirst=True)
    hr_account_status.create(bind, checkfirst=True)

    # ---- hr_users -------------------------------------------------------
    op.add_column(
        "hr_users",
        sa.Column("role", hr_role, nullable=False, server_default="MEMBER"),
    )
    op.add_column(
        "hr_users",
        # existing rows become ACTIVE; the default is switched to PENDING below
        sa.Column("status", hr_account_status, nullable=False, server_default="ACTIVE"),
    )
    op.alter_column("hr_users", "status", server_default="PENDING")

    op.add_column("hr_users", sa.Column("approved_by_id", sa.Integer(), nullable=True))
    op.add_column("hr_users", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "hr_users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_foreign_key(
        "fk_hr_users_approved_by_id",
        "hr_users", "hr_users",
        ["approved_by_id"], ["id"],
        ondelete="SET NULL", onupdate="CASCADE",
    )
    op.create_index(
        "uq_hr_users_one_admin_per_company",
        "hr_users",
        ["company_id"],
        unique=True,
        postgresql_where=sa.text("role = 'ADMIN'"),
    )

    # ---- job_titles -----------------------------------------------------
    op.create_table(
        "job_titles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["hr_users.id"], onupdate="CASCADE", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_titles_company_id"), "job_titles", ["company_id"], unique=False)
    op.create_index(op.f("ix_job_titles_created_by"), "job_titles", ["created_by"], unique=False)
    op.create_index(
        "uq_job_titles_company_lower_name",
        "job_titles",
        ["company_id", sa.text("lower(name)")],
        unique=True,
    )

    # ---- jobs -----------------------------------------------------------
    op.add_column("jobs", sa.Column("job_title_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_jobs_job_title_id",
        "jobs", "job_titles",
        ["job_title_id"], ["id"],
        ondelete="RESTRICT", onupdate="CASCADE",
    )
    op.create_index(op.f("ix_jobs_job_title_id"), "jobs", ["job_title_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_jobs_job_title_id"), table_name="jobs")
    op.drop_constraint("fk_jobs_job_title_id", "jobs", type_="foreignkey")
    op.drop_column("jobs", "job_title_id")

    op.drop_index("uq_job_titles_company_lower_name", table_name="job_titles")
    op.drop_index(op.f("ix_job_titles_created_by"), table_name="job_titles")
    op.drop_index(op.f("ix_job_titles_company_id"), table_name="job_titles")
    op.drop_table("job_titles")

    op.drop_index("uq_hr_users_one_admin_per_company", table_name="hr_users")
    op.drop_constraint("fk_hr_users_approved_by_id", "hr_users", type_="foreignkey")
    for column in (
        "token_version",
        "approved_at",
        "approved_by_id",
        "status",
        "role",
    ):
        op.drop_column("hr_users", column)

    bind = op.get_bind()
    hr_account_status.drop(bind, checkfirst=True)
    hr_role.drop(bind, checkfirst=True)
