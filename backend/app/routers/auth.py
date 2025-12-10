from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from ..database import get_db
from ..models.user import User, Role
from ..schemas.auth import UserCreate, Token
from ..utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    OAuth2 password grant token endpoint.
    Expects form fields: username (email) and password.
    Returns: {"access_token": "<jwt>", "token_type": "bearer"}
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Simple registration endpoint (for development/testing).
    Creates the role if missing and returns a token for the new user.
    """
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    role = db.query(Role).filter(Role.name == payload.role).first()
    if not role:
        role = Role(name=payload.role)
        db.add(role)
        db.commit()
        db.refresh(role)

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency that returns the current user based on the bearer token.
    Raises 401 on invalid token or missing user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        email: Optional[str] = None
        if isinstance(payload, dict):
            email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
    return user


def require_role(role_name: str):
    """
    Dependency factory: requires the current user to have exactly role_name.
    Usage in routers: Depends(require_role("admin"))
    """
    def inner(user: User = Depends(get_current_user)):
        if not user.role or user.role.name != role_name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return inner


def require_any_role(*roles):
    """
    Dependency factory: requires the current user to have any of the provided roles.
    Usage in routers: Depends(require_any_role("admin", "recep"))
    """
    def inner(user: User = Depends(get_current_user)):
        if user.role and user.role.name in roles:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return inner
from fastapi import Depends

@router.get("/me")
def read_current_user(user = Depends(get_current_user)):
    """
    Devuelve el usuario autenticado (para que el frontend conozca rol/email).
    """
    # Devuelve información mínima necesaria por el frontend
    role = None
    if getattr(user, "role", None):
        role = {"name": user.role.name}
    return {"id": user.id, "email": user.email, "role": role, "full_name": getattr(user, "full_name", None)}