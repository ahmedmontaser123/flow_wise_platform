from datetime import datetime
from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship
from .base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_name = Column(String(150), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True, unique=True)

    # Company 1 -> N HR users / Company 1 -> N Jobs
    hr_users = relationship(
        "HRUser",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    jobs = relationship(
        "Job",
        secondary="hr_users",
        back_populates="company",
        viewonly=True,
    )