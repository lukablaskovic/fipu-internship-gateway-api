from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app import schemas
import app.utils as utils
import app.oauth2 as oauth2
from datetime import datetime
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(
    user_credentials: schemas.LoginForm,
    request: Request,  # <- Add this to access the request object
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.email)
        .first()
    )
    if not user:
        logger.warning(
            f"Invalid login attempt: user with email {user_credentials.email} not found."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    if not utils.verify(user_credentials.password, user.password):
        logger.warning(
            f"Invalid login attempt: incorrect password for user with email {user_credentials.email}."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "user_email": user.email},
        remember_me=user_credentials.remember_me,
    )

    # Get client IP address
    client_ip = request.client.host
    logger.info(
        f"User with email {user.email} logged in successfully from IP address {client_ip}."
    )

    # Get current timestamp
    current_timestamp = datetime.now()

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "timestamp": current_timestamp,
    }
