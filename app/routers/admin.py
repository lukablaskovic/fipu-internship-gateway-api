from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2

from app.baserow_service_connector import bw_get_data

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
            response = await bw_get_data("studenti")
            students_from_baserow = response["data"]["results"]

            # 3. Merge the data
            for student in students_from_baserow:
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

            return students_from_baserow

        except Exception as e:
            print("Error fetching and processing students data", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching and processing students data - {e}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


@router.get("/companies", status_code=status.HTTP_200_OK)
async def get_companies_data(
    current_user: models.Admin = Depends(oauth2.get_current_user),
):
    if isinstance(current_user, models.Admin):
        try:
            response = await bw_get_data("firme")
            students = response["data"]["results"]
            return students
        except Exception as e:
            print("Error fetching companies from Baserow", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching companies from Baserow - {e}",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized",
        )
