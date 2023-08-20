from fastapi import status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2

from app.baserow_service_connector import add_student_to_baserow

router = APIRouter(prefix="/students", tags=["Students"])


# Add a new user to Postgres and Baserow
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Student)
async def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    student_data = student.model_dump()

    student_data["password"] = utils.hash(student_data["password"])
    new_student = models.Student(**student_data)

    new_student_baserow = {
        "name": new_student.name,
        "surname": new_student.surname,
        "jmbag": new_student.jmbag,
        "email": new_student.email,
        "year_of_study": new_student.year_of_study,
    }
    # ADD to Baserow
    try:
        response = await add_student_to_baserow(new_student_baserow)
        new_student_baserow_id = response["data"]["id"]
        new_student.baserow_id = new_student_baserow_id
    except Exception as e:
        print("Error adding user to Baserow", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding user to Baserow - {e}",
        )
    try:
        # ADD to Postgres
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
    except Exception as e:
        print("Error adding user to Postgres", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding user to Postgres",
        )
    del new_student.password
    return new_student
