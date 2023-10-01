from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, user, student, admin

from app.db import engine, get_db
from app import models
import app.db
from sqlalchemy.orm import Session

app = FastAPI()
import os, sys
import time
from datetime import datetime


models.Base.metadata.create_all(bind=engine)


"""origins = [
    "http://localhost:5173",
]"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
async def status_check():
    """
    Health check endpoint to monitor the status of the service.
    Returns a 200 status code with a JSON payload if the service is running.
    """
    return {
        "microservice": "internship-gateway-api",
        "status": "OK",
        "message": "Service is running",
        "status_check_timestamp": datetime.now(),
    }


@app.post("/restart")
async def restart_server():
    """
    Handler to restart the server.
    """
    print("Restarting server...")
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "9001",
        ],
    )


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(student.router)
app.include_router(admin.router)


# conda activate fipu-internship-gateway-api
# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 9001
