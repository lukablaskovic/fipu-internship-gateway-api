from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, user, student, admin

from app.db import engine, get_db
from app import models
import app.db
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"msg": "FIPU Internship Gateway API - Running ✅"}


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(student.router)
app.include_router(admin.router)


# conda activate fipu-internship-gateway-api
# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 9001
