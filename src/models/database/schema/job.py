from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.database.base import Base

if TYPE_CHECKING:
    from modules.database.schema.company import Company
    from modules.database.schema.hr_user import HRUser
    from modules.database.schema.job_skill import JobSkill


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_status_end_date", "status", "end_date"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    hr_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("hr_users.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    company_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("company.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    colleges: Mapped[list[str] | None] = mapped_column(JSONB)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    min_years_experience: Mapped[int] = mapped_column(
        Integer, server_default="0"
    )
    status: Mapped[str] = mapped_column(String(20), server_default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    hr_user: Mapped["HRUser"] = relationship()
    company: Mapped["Company"] = relationship()
    job_skills: Mapped[list["JobSkill"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", passive_deletes=True
    )