from abc import ABC, abstractmethod
from enum import Enum

import httpx
from requests import Response, request
from tenacity import retry, stop_after_attempt, wait_fixed


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class CrawlGitBase(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.stars_gte = 100
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    @abstractmethod
    def get_data(self, *args, **kwargs) -> None:  # type: ignore
        ...

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def sync_request(self, method: HttpMethod, url: str, data: dict | None = None, json: dict | None = None, proxies: dict | None = None) -> Response:
        resp = request(method.value, url, data=data, json=json, proxies=proxies)
        return resp

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def async_request(self, method: HttpMethod, url: str, data: dict | None = None, json: dict | None = None, proxies: dict | None = None) -> Response:
        async with httpx.AsyncClient(proxies=proxies) as client:
            resp = await client.request(method.value, url, data=data, json=json)
        return resp
