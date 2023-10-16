# baserow_connector.py

import httpx
from app.config import settings

BASEROW_CONNECTOR_URL = f"{settings.BASEROW_CONNECTOR_URL}/api"


async def BW_add_student_to_baserow(user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASEROW_CONNECTOR_URL}/student", json=user_data)
        response.raise_for_status()
        return response.json()


async def BW_get_data(table_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASEROW_CONNECTOR_URL}/{table_name}")
        return response.json()


async def BW_delete_student_by_email(value: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASEROW_CONNECTOR_URL}/student/email/{value}")
        # print(response)
        return response.json()
