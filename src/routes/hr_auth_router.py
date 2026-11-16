from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from controllers.hr_auth_controller import HRAuthController
from helpers.rbac import CurrentHRUser, DBSession
from schema.hr_auth_schema import (
    AdminRegisterRequest,
    ChangePasswordRequest,
    HRUserOut,
    TokenResponse,
)

hr_auth_router = APIRouter(prefix="/api/v1/hr/auth", tags=["HR - Auth"])


@hr_auth_router.post(
    "/register-admin",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a company and its HR Admin (public)",
)
async def register_admin(data: AdminRegisterRequest, session: DBSession):
    return await HRAuthController(session).register_admin(data)


@hr_auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in (HR Admin or HR Member). Use the email as `username`",
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DBSession,
):
    return await HRAuthController(session).login(form.username, form.password)


@hr_auth_router.get("/me", response_model=HRUserOut, summary="Current HR account")
async def me(current: CurrentHRUser):
    return current


@hr_auth_router.post(
    "/change-password",
    response_model=TokenResponse,
    summary="Change own password (returns a new token, old tokens stop working)",
)
async def change_password(
    data: ChangePasswordRequest, current: CurrentHRUser, session: DBSession
):
    return await HRAuthController(session).change_password(current, data)
