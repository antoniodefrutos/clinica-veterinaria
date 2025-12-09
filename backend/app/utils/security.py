# backend/app/utils/security.py
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

SECRET_KEY = os.getenv("CLINICA_SECRET_KEY", "dev_fallback_change_me")
ALGORITHM = os.getenv("CLINICA_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("CLINICA_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

# Use pbkdf2_sha256 as default to avoid bcrypt 72-byte limitation
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
