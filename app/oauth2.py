from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import jwt
from jose import JWTError

from datetime import datetime, timedelta

import app.db as db
import app.schemas as schemas
import app.models as models

from sqlalchemy.orm import Session

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.PASS_HASHING_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REMEMBER_ME_EXPIRE_MINUTES = settings.REMEMBER_ME_EXPIRE_MINUTES


def create_access_token(data: dict, remember_me: bool = False):
    to_encode = data.copy()

    if remember_me:
        expire_time = datetime.utcnow() + timedelta(minutes=REMEMBER_ME_EXPIRE_MINUTES)
    else:
        expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire_time})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        user_email = payload.get("user_email")
        if id is None and user_email is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=id, user_email=user_email)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(db.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.user_id).first()
    return user
