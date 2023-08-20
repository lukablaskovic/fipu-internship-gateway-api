from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Admin)
async def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    admin_data = admin.model_dump()
    admin_data["password"] = utils.hash(admin_data["password"])
    new_admin = models.Admin(**admin_data)

    try:
        # ADD to Postgres
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
    except Exception as e:
        print("Error adding admin to Postgres", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding admin to Postgres",
        )
    del new_admin.password
    return new_admin


@router.get("/me", status_code=status.HTTP_200_OK, response_model=schemas.Admin)
def get_current_user(
    db: Session = Depends(get_db),
    current_user: schemas.Admin = Depends(oauth2.get_current_user),
):
    return current_user
