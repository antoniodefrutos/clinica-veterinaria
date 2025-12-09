from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
#SECRET_KEY:-------------------------------
SECRET_KEY = "malaspulgas"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 día
# -----------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Password utils
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT utils
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials") from e


# Role/permission helpers (simple pattern)
from typing import Callable

def require_role(role_name: str) -> Callable:
    """
    Dependencia: Depends(require_role("admin"))
    Importa get_current_user _localmente_ desde routers.auth para evitar circular imports.
    """
    # import local para evitar circular imports
    from app.routers.auth import get_current_user  # import lazy, rompe ciclo

    def _dependency(current_user = Depends(get_current_user)):
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        # si tu modelo de usuario usa role_id en vez de role, ajusta aquí
        user_role = getattr(current_user, "role", None) or getattr(current_user, "role_name", None)
        if user_role != role_name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
        return current_user

    return _dependency


def require_admin():
    return require_role("admin")


