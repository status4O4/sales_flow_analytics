import logging
import asyncio
import aiohttp
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self.base_url: str = "https://jsonplaceholder.typicode.com/"
        self._reference_count: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self) -> None:
        async with self._lock:
            if self._reference_count == 0:
                self._session = aiohttp.ClientSession()
                logger.info(
                    f"AsyncHTTPClient session created. reference_count={self._reference_count + 1}"
                )
            else:
                logger.info(
                    f"AsyncHTTPClient session received. reference_count={self._reference_count + 1}"
                )
            self._reference_count += 1

    async def disconnect(self) -> None:
        async with self._lock:
            if self._reference_count > 0:
                self._reference_count -= 1
                if self._reference_count == 0 and self._session:
                    try:
                        await self._session.close()
                    except Exception as err:
                        logging.warning(err)
                    finally:
                        self._session = None
                        logger.info(
                            f"AsyncHTTPClient session closed. reference_count={self._reference_count}"
                        )

    async def get(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            if not self._session:
                logger.error("Session is not initialized. Call connect() first.")
                return None

            url = (
                f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
                if endpoint
                else self.base_url
            )

            logger.debug(f"Making GET request to: {url}")

            async with self._session.get(
                url, params=params, headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"GET request successful: {url}")
                    return data
                else:
                    logger.error(
                        f"GET request failed: {response.status} - {await response.text()}"
                    )
                    return None

        except aiohttp.ClientError as err:
            logger.error(f"HTTP client error during GET request: {err}")
            return None
        except asyncio.TimeoutError:
            logger.error("GET request timeout")
            return None
        except Exception as err:
            logger.error(f"Unexpected error during GET request: {err}")
            return None
