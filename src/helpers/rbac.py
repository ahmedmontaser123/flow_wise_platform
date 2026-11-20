"""Role-Based Access Control dependencies.

Usage (router level):
    router = APIRouter(dependencies=[Depends(require_admin)])

Usage (route level, when you need the user object):
    async def handler(current: CurrentAdmin): ...

Every request reloads the user from the database, so approving, declining,
disabling, deleting or changing a password takes effect immediately -- the
role inside the token is never trusted on its own.
"""
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.connection_database import get_db_session
from models.db.flow_wise.schema import HRUser
# Registers JobTitle on Base.metadata for every HR request, even before
# models/db/flow_wise/schema/__init__.py imports it (see HR_INTEGRATION.md).
from models.db.flow_wise.schema.job_title import JobTitle  # noqa: F401
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from repositories.hr_account_repository import HRAccountRepository
from helpers.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/hr/auth/login")

DBSession = Annotated[AsyncSession, Depends(get_db_session)]

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_hr_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: DBSession,
) -> HRUser:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _CREDENTIALS_ERROR

    user = await HRAccountRepository(session).get_by_id(user_id)
    if user is None:
        raise _CREDENTIALS_ERROR

    # Token must match the current state of the account.
    if (
        payload.get("tv") != user.token_version
        or payload.get("role") != user.role.value
        or payload.get("cid") != user.company_id
    ):
        raise _CREDENTIALS_ERROR

    if user.status != HRAccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    return user


def require_roles(*allowed: HRRole):
    """Dependency factory: allow only the given roles."""

    async def _checker(
        user: Annotated[HRUser, Depends(get_current_hr_user)],
    ) -> HRUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return _checker


require_admin = require_roles(HRRole.ADMIN)
# التعديل هنا: نسمح للمدير بالمرور في أي مسار يتطلب عضو
require_member = require_roles(HRRole.MEMBER, HRRole.ADMIN) 
require_any_hr = require_roles(HRRole.ADMIN, HRRole.MEMBER)

CurrentHRUser = Annotated[HRUser, Depends(require_any_hr)]
CurrentAdmin = Annotated[HRUser, Depends(require_admin)]
CurrentMember = Annotated[HRUser, Depends(require_member)]