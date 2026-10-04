from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from models.enums import ApplicationStatus

from .base import Base


class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "cv_file_id",
            "job_id",
            name="uq_application_cv_job",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    cv_file_id = Column(Integer,ForeignKey("cv_files.id",ondelete="RESTRICT",onupdate="CASCADE",),nullable=False,index=True)
    job_id = Column(Integer,ForeignKey("jobs.id",ondelete="CASCADE",onupdate="CASCADE",),nullable=False,index=True)
    status = Column(SQLEnum(ApplicationStatus,name="application_status"),nullable=False,default=ApplicationStatus.NOT_RECEIVED)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    cv_file = relationship("CvFile",back_populates="applications")

    job = relationship(
        "Job",
        back_populates="applications",
    )