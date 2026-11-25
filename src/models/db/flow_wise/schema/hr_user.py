from datetime import datetime , timezone

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import relationship

from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from .base import Base


class HRUser(Base):
    __tablename__ = "hr_users"
    __table_args__ = (
        # only ONE admin per company (same index as migration c3f1a9e7b2d4)
        Index(
            "uq_hr_users_one_admin_per_company",
            "company_id",
            unique=True,
            postgresql_where=text("role = 'ADMIN'"),
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    role = Column(SQLEnum(HRRole, name="hr_role"), nullable=False, default=HRRole.MEMBER, server_default="MEMBER")
    status = Column(SQLEnum(HRAccountStatus, name="hr_account_status"), nullable=False, default=HRAccountStatus.PENDING, server_default="PENDING")
    approved_by_id = Column(Integer, ForeignKey("hr_users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    token_version = Column(Integer, nullable=False, default=0, server_default="0")

    company = relationship("Company", back_populates="hr_users")
    jobs = relationship(
        "Job",
        back_populates="hr_user",
        cascade="all, delete-orphan",
    )