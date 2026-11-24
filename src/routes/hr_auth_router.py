from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from controllers import HRAuthController
from schema import  AdminRegisterRequest,AdminAccountIn
from models.db.flow_wise.schema import HRUser
from sqlalchemy.ext.asyncio import AsyncSession
from schema import TokenResponse,AdminRegisterRequest,HRUserOut,ChangePasswordRequest
from models.db.connection_database import get_db_session
from dependencies import get_current_hr
from helpers import get_settings
import logging
logger = logging.getLogger(__name__)


hr_auth_router = APIRouter(prefix="/api/v1/hr/auth", tags=["HR - Auth"])

CurrentHRUser = Annotated[
    HRUser,
    Depends(get_current_hr)
]


@hr_auth_router.post(
    "/register-admin",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a company and its HR Admin (public)",
)
async def register_admin(data: AdminRegisterRequest, session:AsyncSession = Depends(get_db_session)):
    logger.info("Register admin endpoint called")
    logger.info("Received registration data: %s", data.model_dump())

    
    settings = get_settings()
    return await HRAuthController(session,settings).register_admin(data)


@hr_auth_router.post("/login",response_model=TokenResponse,summary="Log in (HR Admin or HR Member). Use the email as `username`")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session:AsyncSession = Depends(get_db_session)
):
     settings = get_settings()
     return await HRAuthController(session,settings).login(
          form.username, form.password
     )


@hr_auth_router.get("/me", response_model=HRUserOut, summary="Current HR account")
async def me(current: CurrentHRUser):
    return current


@hr_auth_router.post(
     "/change-password",
     response_model=TokenResponse,
     summary="Change own password (returns a new token, old tokens stop working)",
 )
async def change_password(
    data: ChangePasswordRequest, current: CurrentHRUser, session:AsyncSession = Depends(get_db_session)
 ):
     setting = get_settings()
     return await HRAuthController(session,setting).change_password(current, data)
