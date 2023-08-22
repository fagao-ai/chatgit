from abc import ABC, abstractmethod
from enum import Enum

from requests import request
from tenacity import retry, stop_after_attempt, wait_fixed


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class CrawlGitBase(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.stars_gte = 100
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    @abstractmethod
    def gat_data(self, *args, **kwargs):
        ...

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def request(self, method: HttpMethod, url: str, data: dict = None, json: dict = None, proxies: dict = None):
        resp = request(method.value, url, data=data, json=json, proxies=proxies)
        return resp
