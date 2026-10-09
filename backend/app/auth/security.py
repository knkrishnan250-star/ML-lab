from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def hash_password(password):
    return pwd.hash(password)

def verify_password(password, hashed):
    return pwd.verify(password, hashed)

def create_token(subject):
    payload = {"sub": subject, "exp": datetime.utcnow() + timedelta(hours=8)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def decode_token(token):
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
