
from passlib.context import CryptContext
from passlib.exc import InvalidHashError


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# Dummy hash for timing protection
_DUMMY_HASH = pwd_context.hash(
    "flowwise-dummy-password"
)

def hash_password(plain_password: str) -> str:
    """Hash password before storing it in database."""
    return pwd_context.hash(plain_password)

def verify_password(
    plain_password: str,
    hashed_password: str | None
) -> bool:
    """Verify password against stored hash."""

    if not hashed_password:
        burn_dummy_verify(plain_password)
        return False

    try:
        return pwd_context.verify(
            plain_password,
            hashed_password
        )

    except (InvalidHashError, ValueError):
        return False

def burn_dummy_verify(plain_password: str) -> None:
    """Perform dummy verification for unknown email."""
    pwd_context.verify(
        plain_password,
        _DUMMY_HASH
    )
