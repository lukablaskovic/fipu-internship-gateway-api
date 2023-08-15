# baserow_connector.py

import httpx

BASE_ROW_CONNECTOR_URL = "http://localhost:8080"


async def add_student_to_baserow(user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_ROW_CONNECTOR_URL}/students", json=user_data
        )
        return response.json()
