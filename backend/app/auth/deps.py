from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def current_user(token: str = Depends(oauth2_scheme)):
    try:
        return decode_token(token)["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
