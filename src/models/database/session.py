from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from modules.database.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # ÙŠØªØ£ÙƒØ¯ Ø¥Ù† Ø§Ù„Ø§ØªØµØ§Ù„ Ø´ØºØ§Ù„ Ù‚Ø¨Ù„ Ù…Ø§ ÙŠØ³ØªØ®Ø¯Ù…Ù‡
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency Ø¨ØªØ§Ø¹Ø© FastAPI: Ø¨ØªÙØªØ­ session ÙˆØªÙ‚ÙÙ„Ù‡Ø§ Ø¨Ø¹Ø¯ Ø§Ù„Ù€request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()