from fastapi import HTTPException, status


def not_found(what: str) -> HTTPException:
    # 404 is also used for "exists, but in another company" so IDs cannot be probed.
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{what} not found")


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def unauthorized(detail: str = "Incorrect email or password") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
