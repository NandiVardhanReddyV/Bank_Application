import os
from dotenv import load_dotenv
import hashlib
import bcrypt
import base64
from datetime import datetime,timedelta,timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET KEY not set in environment")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

IST = timezone(timedelta(hours = 5,minutes = 30))
# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

# --OAuth2 scheme (reads Bearer token from Authorization header) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login")

# ---Pydantic models ---
class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username : str
    password : str

class UserResponse(BaseModel):
    id: str
    username: str

# --- Helpers ---
def _prepare_password(password : str) -> str:
    """Pre-hash with SHA-256 to bypass bcrypt's 72-byte limit.
      bcrypt receives a fixed 44-char base 64 string regardless of input length
      """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)

def hash_password(password : str) -> str:
    prepared = _prepare_password(password)
    hashed = bcrypt.hashpw(prepared,bcrypt.gensalt(rounds = 12)) # round = 12 is secure default
    return hashed.decode("utf-8")

def verify_password(plain : str,hashed: str) -> bool:
    prepared = _prepare_password(plain)
    return bcrypt.checkpw(prepared,hashed.encode("utf-8"))
    #return pwd_context.verify(prepared,hashed)

def create_access_token(data : dict,expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes = 15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm = ALGORITHM)

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms =[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code = 401,detail = "Invalid token payload")
        return TokenData(username = username)
    except JWTError:
        raise HTTPException(status_code = 401,detail = "Invalid or expired token")
    
