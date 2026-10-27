from sqlalchemy import (
    Boolean,
    Column,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Text,
    DateTime
)
from datetime import datetime , timezone
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base



class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    last_edited = Column(
        DateTime, nullable=False , default=datetime.now(timezone.utc)
    )
    
    schema_definition = Column(
        JSONB, nullable=False
    )    
    weight = Column(
        Float,
        default=1.0,
        nullable=False,
    )

    # Relationship
    job = relationship(
        "Job",
        back_populates="requirements",
    )
