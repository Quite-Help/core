from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import ActivateAccountRequest, LoginRequest, LoginResponse, RegisterAccountRequest
from app.repositories.base_repo import get_db
from app.core.config import settings
from app.core.security import check_auth, hash_password, verify_password
from app.schema.account import Account, Role

router = APIRouter(prefix="/account", tags=["Account"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60


@router.post("/token", response_model=LoginResponse)
async def get_token(
    body: LoginRequest = Depends(), db: AsyncSession = Depends(get_db)
):
    account = (await db.scalars(select(Account).where(Account.username == body.username))).first()
    if not account or not verify_password(body.password, account.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": str(account.id),
        "roles": account.roles,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return LoginResponse(access_token=token)


@router.post("/register")
def register_account(body: RegisterAccountRequest, db: AsyncSession = Depends(get_db), _ = Depends(check_auth([Role.SUPER_ADMIN]))):
    '''
    TODO: create an account creation link with a activation_secret token and store token in the database mapped to the roles provided then send an account creation invite email
    link will send users to the front end app yet to be implemented
    
    NOTE: make sure there is only one active activation_secret per email
    '''
    pass

@router.post("/activate")
def activate_account(body: ActivateAccountRequest, db: AsyncSession = Depends(get_db)):
    '''
    TODO: check if activation_secret matches an unused record in the database
    if there is a match create an account with the display_name, username and hashed password with roles associated with the activation_secret
    if there is no match raise an HTTPException with 403 forbiden message
    '''
    pass

@router.post("/tmp/bootstrap")
async def bootstrap_core_api_with_an_account_with_all_roles(db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(Account).where(Account.username == "admin"))).scalar_one_or_none():
        return
    password_hash = hash_password("admin")
    new_account = Account(
        username='admin',
        password=password_hash,
        display_name='Admin'
    )
    new_account.add_role(Role.ADMIN)
    new_account.add_role(Role.SUPER_ADMIN)
    new_account.add_role(Role.SERVICE)
    db.add(new_account)
