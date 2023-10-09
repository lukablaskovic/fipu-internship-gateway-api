# baserow_connector.py

import httpx
from app.config import settings

BPMN_ENGINE_CONNECTOR_URL = f"${settings.BPMN_ENGINE_URL}"


async def BE_remove_instance_by_id(instance_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BPMN_ENGINE_CONNECTOR_URL}/instance/{instance_id}"
        )
        return response.json()
