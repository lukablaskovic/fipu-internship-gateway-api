# baserow_connector.py

import httpx

BPMN_ENGINE_CONNECTOR_URL = "http://localhost:9000"


async def BE_remove_instance_by_id(instance_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BPMN_ENGINE_CONNECTOR_URL}/instance/{instance_id}"
        )
        return response.json()
