from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2

import logging
from app.connectors.baserow_service_connector import (
    BW_get_data,
    BW_delete_student_by_email,
)
from app.connectors.bpmn_engine_service_connector import BE_remove_instance_by_id

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        logger.error(f"Error adding admin to Postgres: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding admin to Postgres",
        )
    del new_admin.password
    logger.info(f"Admin with email {new_admin.email} created successfully.")
    return new_admin


@router.get("/students", status_code=status.HTTP_200_OK)
async def get_students_data(
    db: Session = Depends(get_db),
    current_user: models.Admin = Depends(oauth2.get_current_user),
):
    if isinstance(current_user, models.Admin):
        try:
            # 1. Fetch the required fields from PostgreSQL
            db_students = db.query(
                models.Student.id,
                models.Student.baserow_id,
                models.Student.process_instance_id,
            ).all()
            db_students_dict = {
                student.baserow_id: {
                    "postgres_id": student.id,
                    "process_instance_id": student.process_instance_id,
                }
                for student in db_students
            }

            # 2. Fetch data from Baserow
            response = await BW_get_data("Student")
            students_data = response["data"]["results"]

            # 3. Merge the data
            for student in students_data:
                student_baserow_id = student.get("id")
                if student_baserow_id in db_students_dict:
                    student["process_instance_id"] = db_students_dict[
                        student_baserow_id
                    ]["process_instance_id"]
                    student["postgres_id"] = db_students_dict[student_baserow_id][
                        "postgres_id"
                    ]
                else:
                    pass

            logger.info("Successfully fetched and processed students data.")
            return students_data

        except Exception as e:
            logger.error(f"Error fetching and processing students data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching and processing students data - {e}",
            )
    else:
        logger.warning("Unauthorized access attempt to get students data.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


@router.delete("/students/{email}", status_code=status.HTTP_200_OK)
async def delete_student(
    email: str,
    db: Session = Depends(get_db),
    current_user: models.Admin = Depends(oauth2.get_current_user),
):
    if not isinstance(current_user, models.Admin):
        logger.warning("Unauthorized access attempt to delete student.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        # 1. Delete the student from Baserow
        baserow_response = await BW_delete_student_by_email(email)

        if not baserow_response or baserow_response.get("status") != True:
            raise Exception("Error deleting student from Baserow")
        else:
            logger.info(f"Student {email} deleted from Baserow!")

        # 2. Retrieve the process instance ID for the student from Postgres
        student = db.query(models.Student).filter(models.Student.email == email).first()

        if not student:
            logger.warning("Student not found in Postgres.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found in Postgres.",
            )

        process_instance_id = student.process_instance_id
        bpmn_engine_response = await BE_remove_instance_by_id(process_instance_id)
        logger.info(f"Process instance {process_instance_id} deleted from BPMN Engine!")

        # 3. Delete the student from Postgres
        student = db.query(models.Student).filter(models.Student.email == email).first()

        if not student:
            logger.warning("Student not found in Postgres.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found in Postgres.",
            )

        db.delete(student)
        db.commit()
        logger.info(f"Student {email} deleted from Postgres!")

    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting student - {e}",
        )

    return {"detail": "Student deleted successfully"}


class AvatarUpdate(BaseModel):
    avatar_url: str


@router.patch("/avatar", status_code=status.HTTP_200_OK)
async def update_admin_avatar(
    username: str,
    avatar_update: AvatarUpdate,
    db: Session = Depends(get_db),
    current_user: models.Admin = Depends(oauth2.get_current_user),
):
    if not isinstance(current_user, models.Admin):
        logger.warning("Unauthorized access attempt to update admin avatar.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        admin = db.query(models.Admin).filter(models.Admin.username == username).first()

        if not admin:
            logger.warning("Admin not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found",
            )

        admin.avatar = avatar_update.avatar_url
        db.commit()
        db.refresh(admin)
        logger.info(f"Avatar updated successfully for admin with username {username}.")

    except Exception as e:
        logger.error(f"Error updating admin avatar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating admin avatar - {str(e)}",
        )

    return {"detail": "Avatar updated successfully"}
