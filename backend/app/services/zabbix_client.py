from app.core.config import settings
from app.core.logging import get_logger
import httpx

logger = get_logger(__name__)


class ZabbixClient:
    def __init__(self):
        self.url = settings.ZABBIX_URL
        self.token = settings.ZABBIX_API_TOKEN

    async def get_host_info(self, host_id: str) -> dict | None:
        if not self.url or not self.token:
            logger.debug("Zabbix not configured, skipping host info fetch")
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.url}/api_jsonrpc.php",
                    json={
                        "jsonrpc": "2.0",
                        "method": "host.get",
                        "params": {"hostids": [host_id], "output": "extend"},
                        "auth": self.token,
                        "id": 1,
                    },
                    timeout=10,
                )
                data = resp.json()
                if data.get("result"):
                    return data["result"][0]
        except Exception as e:
            logger.error("Failed to fetch host info from Zabbix: %s", str(e))
        return None
