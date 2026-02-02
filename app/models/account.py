from pydantic import BaseModel, EmailStr

from app.schema.account import Role


class LoginResponse(BaseModel):
    access_token: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterAccountRequest(BaseModel):
    email: EmailStr
    roles: list[Role]

class ActivateAccountRequest(BaseModel):
    activation_secret: str
    display_name: str
    username: str
    password: str