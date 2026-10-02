from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.database.base import Base

if TYPE_CHECKING:
    from modules.database.schema.cv import CV


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    education: Mapped[str | None] = mapped_column(String(255))
    portfolio: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(
        String(20), server_default="active"
    )  # account status, not application status

    cvs: Mapped[list["CV"]] = relationship(
        back_populates="candidate", cascade="all, delete-orphan", passive_deletes=True
    )