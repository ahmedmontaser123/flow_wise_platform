from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from models.enums import ParsingStatus

from .base import Base


class CvParsed(Base):
    __tablename__ = "cv_parsed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_file_id = Column(
        Integer,
        ForeignKey("cv_files.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    parsed_data = Column(JSON, nullable=True)
    status = Column(SQLEnum(ParsingStatus), nullable=False, default=ParsingStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships
    # CvFile 1 -> 1 CvParsed
    cv_file = relationship("CvFile", back_populates="parsed")