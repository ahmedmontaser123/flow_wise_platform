from sqlalchemy import (
    Boolean,
    Column,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base
from models.enums import RequirementType


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(SQLEnum(RequirementType), nullable=False)
    content = Column(Text, nullable=False)
    required = Column(Boolean, default=True, nullable=False)
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