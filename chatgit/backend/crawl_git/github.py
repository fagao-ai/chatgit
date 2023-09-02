import asyncio
import base64
import json
from asyncio import Queue
from enum import Enum
from typing import AsyncGenerator, Dict, Set, Tuple

from httpx import Response
from proxybroker2 import Broker, Proxy
from tqdm import tqdm
from tqdm.std import Bar

from chatgit.backend.crawl_git.crawl_git_base import CrawlGitBase, HttpMethod
from chatgit.common import config
from chatgit.common.logger import logger  # types: ignore
from chatgit.models.repositories import Repositories


class CrawlFailStage(str, Enum):
    GET_REPOS = "get_repos"
    GET_CONTENTS = "get_contents"
    GET_README = "get_readme"


class AsyncCrawlGithub(CrawlGitBase):
    def __init__(self) -> None:
        super().__init__("https://api.github.com")
        self.search_base_url = self.base_url + "/search/repositories"
        self.page_bar: Bar = None
        self.repo_bar: Bar = None
        self.repo_index = 0
        self.proxys = config.proxy.proxy.split(";")
        self.proxies: Queue[Proxy] = asyncio.Queue()
        self.available_proxys: Set[str] = set()

    async def find_proxies(self) -> None:
        if self.proxies.empty():
            broker = Broker(self.proxies)
            print("find_proxies")
            await broker.find(types=["HTTP", "HTTPS"], limit=200, lvl="High")
            while broker._all_tasks:
                await asyncio.sleep(1)
            await broker.stop()
            print("stop")

    async def download_readme(self, project_full_name: str) -> Tuple[str, str] | None:
        readme_url = f"{self.base_url}/repos/{project_full_name}/readme"
        response = await self.forever_request_github(readme_url)
        response_data = response.json()
        readme_content = response_data["content"]
        readme_name = response_data["name"]
        decoded_content = base64.b64decode(readme_content).decode("utf-8")
        return decoded_content, readme_name

    async def forever_request_github(self, url: str) -> Response:
        while True:
            proxy_dict = await self.get_proxy()

            try:
                proxies = {
                    "http://": proxy_dict["http"],
                    "https://": proxy_dict["http"],
                }
                resp = await self.async_request(HttpMethod.GET, url, proxies=proxies)
                if resp.status_code == 200:
                    self.available_proxys.add(proxy_dict["http"])
                    return resp
                self.available_proxys.remove(proxy_dict["http"])
                await asyncio.sleep(0.1)
            except Exception:
                self.available_proxys.remove(proxy_dict["http"])
                await asyncio.sleep(0.1)
                continue

    async def get_proxy(self) -> Dict[str, str]:
        if self.available_proxys:
            http_proxy = self.available_proxys.pop()
            return {"http": http_proxy}
        if not self.proxies.empty():
            proxy = await self.proxies.get()
            http_proxy = f"http://{proxy.host}:{proxy.port}"
            return {"http": http_proxy}
        print("proxies queue is empty!!!")
        await self.find_proxies()
        return await self.get_proxy()

    async def get_data(self, page_size: int = 100) -> AsyncGenerator[Repositories, None]:  # type: ignore
        total_count = await self.get_total_repo()
        total_page = int(total_count / page_size) + 1
        self.page_bar = tqdm(range(1, total_page + 1), desc="page1: ", total=total_page)
        for page in self.page_bar:
            query_param_str = f"stars:>={self.stars_gte}&sort=stars&per_page={page_size}&page={page}"
            url = self.search_base_url + "?q=" + query_param_str
            repo_resp = await self.forever_request_github(url)
            repos = repo_resp.json().get("items")
            if repos is None:
                logger.failure(
                    json.dumps(
                        {
                            "url": url,
                            "failure_stage": CrawlFailStage.GET_REPOS.value,
                            "meta_info": {},
                            "error_msg": repo_resp.json(),
                        }
                    )
                )
                continue
            self.repo_bar = tqdm(repos, desc="repos0 -> start: ", total=len(repos))
            for repo_json in self.repo_bar:
                self.repo_index += 1
                id = repo_json["id"]
                name = repo_json["name"]
                full_name = repo_json["full_name"]
                index_url = repo_json["html_url"]
                api_url = repo_json["url"]
                description = repo_json["description"]
                language = repo_json["language"]
                has_wiki = repo_json["has_wiki"]
                forks_count = repo_json["forks_count"]
                license = repo_json["license"]  # json
                topics = repo_json["topics"]  # list
                repo_info = {
                    "repo_id": id,
                    "name": name,
                    "full_name": full_name,
                    "index_url": index_url,
                    "api_url": api_url,
                    "description": description,
                    "language": language,
                    "has_wiki": has_wiki,
                    "forks_count": forks_count,
                    "license": license,
                    "topics": topics,
                }
                readme_tuple = await self.download_readme(full_name)
                if readme_tuple is None:
                    continue
                readme_content, readme_name = readme_tuple
                repo_info["readme_content"] = readme_content
                repo_info["readme_name"] = readme_name
                yield Repositories(**repo_info)
                self.repo_bar.set_description(f"repo{self.repo_index} -> success")
            self.page_bar.set_description(f"page{page}")

    async def get_total_repo(self) -> int:
        url = self.search_base_url + "?q=" + f"stars:>={self.stars_gte}"
        resp = await self.forever_request_github(url)
        data_json = resp.json()
        return data_json["total_count"]


if __name__ == "__main__":

    async def run_async_crawl() -> None:
        crawl_github = AsyncCrawlGithub()
        async for repo in crawl_github.get_data(page_size=100):
            print(repo)

        # await crawl_github.get_data(page_size=100)

    asyncio.run(run_async_crawl())
