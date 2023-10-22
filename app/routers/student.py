from fastapi import status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import httpx
import logging
from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2
from app.routers.default_avatar import avatar
from app.connectors.baserow_service_connector import BW_add_student_to_baserow

router = APIRouter(prefix="/students", tags=["Students"])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Add a new user to Postgres and Baserow
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    student_data = student.model_dump()

    student_data["password"] = utils.hash(student_data["password"])
    new_student = models.Student(**student_data)

    new_student_baserow = {
        "ime": new_student.ime,
        "prezime": new_student.prezime,
        "JMBAG": new_student.JMBAG,
        "email": new_student.email,
        "godina_studija": new_student.godina_studija,
        "avatar": avatar,
    }

    # ADD to Baserow
    try:
        response = await BW_add_student_to_baserow(new_student_baserow)
        new_student_baserow_id = response["data"]["id"]
        new_student.baserow_id = new_student_baserow_id
    except httpx.HTTPStatusError as exc:
        error_response = exc.response.json()
        logger.error(
            f"Error adding user to Baserow: {error_response.get('error', 'Unknown error from Baserow')}"
        )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=error_response.get("error", "Unknown error from Baserow"),
        )
    except Exception as e:
        logger.error(f"Error adding user to Baserow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding user to Baserow - {e}",
        )

    # ADD to Postgres
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
    except IntegrityError:
        logger.error(f"Unique constraint violated for student: {student_data}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student je već registriran u sustavu.",
        )
    except Exception as e:
        logger.error(f"Error adding user to Postgres: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding user to Postgres",
        )
    del new_student.password
    pydantic_student = schemas.Student(**new_student.__dict__)

    return {
        "data": pydantic_student,
        "message": "Student uspješno dodan.",
        "status": 201,
    }


@router.patch("/{student_id}/process-instance", status_code=status.HTTP_200_OK)
async def update_process_instance(
    student_id: int,
    process_update: schemas.ProcessInstanceUpdate,
    db: Session = Depends(get_db),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student nije pronađen."
        )
    logger.info(f"Process instance ID: {process_update.process_instance_id}")
    student.process_instance_id = process_update.process_instance_id

    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error updating process instance ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating process instance ID - {e}",
        )

    return {"message": "Process instance ID updated successfully"}
