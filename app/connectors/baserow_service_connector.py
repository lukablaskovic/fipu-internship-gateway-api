# baserow_connector.py

import httpx

BASE_ROW_CONNECTOR_URL = "http://localhost:8080"


async def bw_add_student_to_baserow(user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_ROW_CONNECTOR_URL}/students", json=user_data
        )
        return response.json()


async def bw_get_data(table_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_ROW_CONNECTOR_URL}/{table_name}")
        return response.json()


async def bw_delete_student_by_email(value: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_ROW_CONNECTOR_URL}/students/email/{value}"
        )
        return response.json()
