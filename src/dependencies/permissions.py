
from typing import Annotated
from fastapi import Depends, HTTPException, status
from dependencies.auth import get_current_hr
from models.enums import HRRole


def require_roles(*allowed_roles: HRRole):

    async def role_checker(
        current_hr: Annotated[
            object,
            Depends(get_current_hr)
        ],
    ):

        if current_hr.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action",
            )

        return current_hr

    return role_checker
