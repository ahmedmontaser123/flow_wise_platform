
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RequirementType(Base):
    __tablename__ = "requirement_types"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(120), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id", "name",
            name="uq_requirement_type_company_name",
        ),
        UniqueConstraint(
            "company_id", "id",
            name="uq_requirement_type_company_id",
        ),
    )


class RequirementTypeVersion(Base):
    __tablename__ = "requirement_type_versions"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    type_id: Mapped[int] = mapped_column(
        ForeignKey("requirement_types.id"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    schema_definition: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False
    )
    matching_rules: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False
    )
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __table_args__ = (
        UniqueConstraint(
            "type_id", "version",
            name="uq_requirement_type_version",
        ),
        CheckConstraint(
            "version > 0", name="ck_type_version_positive"
        ),
    )


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    type_version_id: Mapped[int] = mapped_column(
        ForeignKey("requirement_type_versions.id"),
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False
    )
    required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    weight: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    __table_args__ = (
        CheckConstraint(
            "weight >= 0 AND weight <= 1",
            name="ck_requirement_weight_range",
        ),
        CheckConstraint(
            "position >= 0",
            name="ck_requirement_position_nonnegative",
        ),
        Index("ix_job_requirements_job", "job_id"),
    )


class CandidateAttribute(Base):
    __tablename__ = "candidate_attributes"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
    )
    type_version_id: Mapped[int] = mapped_column(
        ForeignKey("requirement_type_versions.id"),
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False
    )

    __table_args__ = (
        Index(
            "ix_candidate_attributes_candidate_type",
            "candidate_id", "type_version_id",
        ),
    )