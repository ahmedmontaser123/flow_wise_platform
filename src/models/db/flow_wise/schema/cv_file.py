from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class CvFile(Base):
    __tablename__ = "cv_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships
    # candidates 1 -> N CV / CV 1 -> 1 parsed / CV 1 -> N Application
    candidate = relationship("Candidate", back_populates="cvs")
    parsed = relationship(
        "CvParsed",
        back_populates="cv_file",
        uselist=False,
        cascade="all, delete-orphan",
    )
    # cv_file_id is ON DELETE RESTRICT on applications, so a CV that is still
    # referenced cannot be deleted -- no delete-orphan cascade here on purpose.
    applications = relationship("Application", back_populates="cv_file")