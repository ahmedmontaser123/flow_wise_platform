from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.enums import CandidateStatus

from .base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    education = Column(String(255), nullable=True)
    portfolio = Column(String(500), nullable=True)
    status = Column(SQLEnum(CandidateStatus), nullable=False, default=CandidateStatus.APPLIED)
    #Location
    #JSON

    # Candidate 1 -> N CV / Candidate 1 -> N Applications
    cvs = relationship(
        "CvFile",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    applications = relationship(
        "Application",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )