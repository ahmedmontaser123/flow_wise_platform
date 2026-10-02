from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    DateTime,
    ForeignKey,
    String,
    Text,
    false,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.database.base import Base

if TYPE_CHECKING:
    from modules.database.schema.candidate import Candidate


class CV(Base):
    __tablename__ = "cv"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("candidates.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    file_path: Mapped[str] = mapped_column(String(500))
    file_hash: Mapped[str | None] = mapped_column(CHAR(64))
    raw_extracted_text: Mapped[str | None] = mapped_column(Text)
    is_text_extracted: Mapped[bool] = mapped_column(
        Boolean, server_default=false()
    )
    extraction_status: Mapped[str] = mapped_column(
        String(20), server_default="pending"
    )  # pending, completed, failed
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    parsed_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    parsing_status: Mapped[str] = mapped_column(
        String(20), server_default="pending"
    )
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    candidate: Mapped["Candidate"] = relationship(back_populates="cvs")