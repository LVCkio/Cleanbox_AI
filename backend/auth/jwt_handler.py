"""
CleanInbox AI — JWT Authentication Handler
OAuth2 Password Flow + JWT Bearer Token.
Sử dụng bcrypt trực tiếp (thay passlib bị incompatible với bcrypt 4+).
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from backend.config import settings

# ─── OAuth2 scheme ──────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# ─── Pydantic Schemas ───────────────────────────────
class TokenData(BaseModel):
    org_id: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# ─── Password Hashing (bcrypt trực tiếp) ────────────
def verify_password(plain: str, hashed: str) -> bool:
    """So sánh password với bcrypt hash."""
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )

def get_password_hash(password: str) -> str:
    """Hash password bằng bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT token với payload được ký bằng SECRET_KEY."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_org(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Dependency: decode JWT và trả về TokenData."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        org_id: str = payload.get("org_id")
        email: str = payload.get("sub")
        if org_id is None:
            raise credentials_exception
        return TokenData(org_id=org_id, email=email)
    except JWTError:
        raise credentials_exception
