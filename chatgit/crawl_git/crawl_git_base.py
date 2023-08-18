from abc import abstractmethod, ABC

from requests import request
from tenacity import retry, stop_after_attempt, wait_fixed

from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class CrawlGitBase(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.stars_gte = 100
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    @abstractmethod
    def gat_data(self, *args, **kwargs):
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def request(self, method: HttpMethod, url: str, data: dict, json: dict):
        resp = request(method.value, url, data=data, json=json)
        return resp
