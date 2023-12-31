from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Generator, Union

import httpx
from requests import Response

from chatgit.common import StrEnum
from chatgit.models.repositories import Repositories


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"


class CrawlGitBase(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.stars_gte = 100
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        }

    @abstractmethod
    def get_data(self, *args, **kwargs) -> Union[Generator[int, None, Repositories], AsyncGenerator[None, Repositories]]:  # type: ignore
        ...

    async def async_request(
        self,
        method: HttpMethod,
        url: str,
        data: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
        proxies: Dict[str, Any] | None = None,
    ) -> Response:
        if proxies is None:
            proxies = {}
        async with httpx.AsyncClient(proxies=proxies, timeout=10) as client:
            resp = await client.request(str(method.value), url, data=data, json=json)
        return resp
