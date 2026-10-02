from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.database.base import Base


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    description: Mapped[str | None] = mapped_column(Text)
    company_name: Mapped[str] = mapped_column(String(150), unique=True)
    address: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))

    hr_users: Mapped[list["HRUser"]] = relationship(back_populates="company")