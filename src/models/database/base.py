from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# naming convention: Ø¨ÙŠØ®Ù„ÙŠ Ø£Ø³Ù…Ø§Ø¡ Ø§Ù„Ù€constraints Ø«Ø§Ø¨ØªØ© ÙˆÙ…ØªÙˆÙ‚Ø¹Ø©
# Ø¯Ù‡ Ù…Ù‡Ù… Ø¬Ø¯Ù‹Ø§ Ù„Ù€Alembic Ø¹Ø´Ø§Ù† ÙŠØ¹Ø±Ù ÙŠØ¹Ù…Ù„ downgrade/upgrade ØµØ­
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)