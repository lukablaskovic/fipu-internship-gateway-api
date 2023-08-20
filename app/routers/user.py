from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    if current_user.type == "student":
        student = (
            db.query(models.Student)
            .filter(models.Student.id == current_user.id)
            .first()
        )
        return schemas.Student.model_validate(student.__dict__)
    elif current_user.type == "admin":
        admin = (
            db.query(models.Admin).filter(models.Admin.id == current_user.id).first()
        )
        return schemas.Admin.model_validate(admin.__dict__)
    else:
        raise HTTPException(status_code=400, detail="User type not recognized")
