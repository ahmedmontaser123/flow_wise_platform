from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class JobTitle(Base):
    """A reusable job title in a company's catalog (e.g. "Backend Engineer").

    Postings (the ``jobs`` table) point to a title through ``jobs.job_title_id``.
    A title that is still used by a posting cannot be deleted (ON DELETE RESTRICT).
    """

    __tablename__ = "job_titles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        BigInteger,
        ForeignKey("companies.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(150), nullable=False)
    department = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(
        Integer,
        ForeignKey("hr_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # One-way relationships, so company.py / hr_user.py do not need back_populates.
    company = relationship("Company")
    creator = relationship("HRUser", foreign_keys=[created_by])


# Title names are unique per company, case-insensitive ("Backend Engineer" == "backend engineer").
Index(
    "uq_job_titles_company_lower_name",
    JobTitle.company_id,
    func.lower(JobTitle.name),
    unique=True,
)
