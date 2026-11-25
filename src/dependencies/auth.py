from typing import Annotated

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from helpers.jwt_handler import decode_access_token
from repositories import HRUserRepository
from models.db.connection_database import get_db_session


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/hr/auth/login"
)


async def get_current_hr(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decode JWT
    try:
        payload = decode_access_token(token)
        hr_id = int(payload["sub"])

    except (jwt.PyJWTError, ValueError, KeyError):
        raise credentials_exception

    # 2. Fetch HR from database
    hr = await HRUserRepository(session = db).get_by_id(
        hr_id=hr_id,
    )

    # 3. Check user existence and status
    if hr is None :
        raise credentials_exception

    # 4. Validate token version
    if hr.token_version != payload["tv"]:  
        raise credentials_exception

    return hr