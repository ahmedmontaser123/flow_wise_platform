from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.database.base import Base

if TYPE_CHECKING:
    from modules.database.schema.job import Job
    from modules.database.schema.skill import Skill


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skills_job_id_skill_id"),
        Index("ix_job_skills_job_id_requirement_type", "job_id", "requirement_type"),
        Index("ix_job_skills_skill_id", "skill_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("skills.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    requirement_type: Mapped[str] = mapped_column(String(20))  # must or preferred
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    job: Mapped["Job"] = relationship(back_populates="job_skills")
    skill: Mapped["Skill"] = relationship()