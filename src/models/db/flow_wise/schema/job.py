from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from models.enums import EmployType, ExperienceLevel, JobStatus

from .base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    employment_type = Column(SQLEnum(EmployType), nullable=False)
    experience_level = Column(SQLEnum(ExperienceLevel), nullable=True)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.DRAFT)
    created_by = Column(
        Integer,
        ForeignKey("hr_users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    hr_user = relationship(
        "HRUser",
        back_populates="jobs",
    )
    # reachable through the HR user that owns the job
    company = relationship(
        "Company",
        secondary="hr_users",
        back_populates="jobs",
        uselist=False,
        viewonly=True,
    )
    requirements = relationship(
        "JobRequirement",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",
    )