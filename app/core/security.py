from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from argon2 import PasswordHasher

from app.models.account import Role

http_bearer = HTTPBearer()


def check_auth(required_roles: list[Role] = []):
    def check_auth_internal(security: HTTPAuthorizationCredentials = Depends(http_bearer)):
        try:
            payload = jwt.decode(
                security.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            roles = set(payload.get("roles", []))
            for req_role in required_roles:
                if req_role not in roles:
                    raise HTTPException(status_code=403, detail="Insufficient role")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    return check_auth_internal


ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return ph.verify(hashed, plain)
