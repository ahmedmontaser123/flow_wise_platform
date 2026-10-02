from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.database.base import Base

if TYPE_CHECKING:
    from modules.database.schema.application_status_history import ApplicationStatusHistory
    from modules.database.schema.candidate import Candidate
    from modules.database.schema.cv import CV
    from modules.database.schema.hr_user import HRUser
    from modules.database.schema.job import Job


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "candidate_id", "job_id", name="uq_applications_candidate_id_job_id"
        ),
        Index("ix_applications_job_id_score", "job_id", "score"),
        Index("ix_applications_ats_status", "ats_status"),
        Index("ix_applications_hr_decision", "hr_decision"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("candidates.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    cv_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cv.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    extracted_college: Mapped[str | None] = mapped_column(String(100))
    extracted_years_experience: Mapped[int | None] = mapped_column(Integer)
    critical_rule_passed: Mapped[bool | None] = mapped_column(Boolean)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # 0-100
    match_explanation: Mapped[str | None] = mapped_column(Text)
    ats_status: Mapped[str] = mapped_column(String(20), server_default="pending")
    hr_decision: Mapped[str] = mapped_column(String(20), server_default="pending")
    rejection_cause: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("hr_users.id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    candidate: Mapped["Candidate"] = relationship()
    job: Mapped["Job"] = relationship()
    cv: Mapped["CV"] = relationship()
    reviewer: Mapped["HRUser | None"] = relationship()
    status_history: Mapped[list["ApplicationStatusHistory"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )