from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from passlib.context import CryptContext
from jose import JWTError, jwt

# ---------------------------------------------------------------------
# Configuración seguridad / tokens
# ---------------------------------------------------------------------
SECRET_KEY = "malaspulgas"           # <- tu SECRET_KEY (dev)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 día, ajustar si hace falta

# Usamos pbkdf2_sha256 para evitar dependencias nativas de bcrypt en dev.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ---------------------------------------------------------------------
# Helpers de contraseña
# ---------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    """Hashea una contraseña en texto plano."""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña contra hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------------------------------------------------------
# Helpers JWT
# ---------------------------------------------------------------------
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
# ----------------------------
# FastAPI auth/depends helpers
# ----------------------------
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def _unauth_exc(detail: str = "Could not validate credentials"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodifica el JWT y devuelve el payload.
    Si el token no es válido devuelve 401.
    """
    payload = decode_access_token(token)
    if not payload:
        raise _unauth_exc()
    return payload

def get_current_user_payload(payload: dict = Depends(get_token_payload)) -> dict:
    """
    Devuelve el payload del usuario actual (por conveniencia).
    El payload suele contener 'sub' y 'role' según cómo crees el token.
    """
    return payload

def require_role(role_name: str):
    """
    Factory: devuelve una dependencia que exige que payload['role']==role_name.
    Uso: Depends(require_role('admin'))
    """
    def _dep(payload: dict = Depends(get_current_user_payload)):
        role = payload.get("role")
        if role != role_name:
            raise HTTPException(status_code=403, detail="Operation requires role: %s" % role_name)
        return payload
    return _dep

# Dependencia concreta para admin (usada por informes.py)
require_admin = require_role("admin")

# --- Dependencias / helpers para FastAPI (añadir al final de app/utils/security.py) ---
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

# evita import circular: importa get_db desde tu módulo de db
from ..database import get_db
from ..models.user import User
from jose import JWTError

# reuse oauth2 scheme — el tokenUrl coincide con tu router /auth/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Decodifica token y devuelve el usuario actual de la BDD.
    Levanta 401 si no hay token válido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)  # función que ya deberías tener aquí
        # payload debería contener 'sub' con email
        email: Optional[str] = payload.get("sub") if isinstance(payload, dict) else None
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
    return user

def require_role(role_name: str):
    """
    Dependency factory: exige un role concreto (p. ej. 'admin').
    Uso en router: Depends(require_role('admin'))
    """
    def inner(user: User = Depends(get_current_user)):
        if not getattr(user, "role", None) or user.role.name != role_name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return inner

def require_any_role(*role_names: str):
    """
    Dependency factory: permite varios roles (p. ej. 'admin','receptionist').
    Uso en router: Depends(require_any_role('admin','receptionist'))
    """
    def inner(user: User = Depends(get_current_user)):
        if getattr(user, "role", None) and user.role.name in role_names:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return inner

# conveniencia para admin
require_admin = require_role("admin")