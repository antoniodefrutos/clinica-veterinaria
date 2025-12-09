# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.user import User, Role
from ..schemas.auth import UserCreate, Token, TokenData
from ..utils.security import hash_password, verify_password, create_access_token, decode_access_token
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Token endpoint
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

# Register (dev). Creates role if missing.
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
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
        role_id=role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}

# Utilities (dependencies)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
    return user

def require_role(role_name: str):
    def inner(user: User = Depends(get_current_user)):
        if not user.role or user.role.name != role_name:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return inner


def require_any_role(*roles):
    from fastapi import Depends, HTTPException, status
    def inner(user = Depends(get_current_user)):
        if user.role and user.role.name in roles:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return inner
