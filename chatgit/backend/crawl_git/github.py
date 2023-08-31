import asyncio
import base64
import json
from enum import Enum
from typing import Any, AsyncGenerator, Dict, Tuple

from ratelimit import limits, sleep_and_retry  # types: ignore
from requests import Response
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
    def __init__(self, proxies: Dict[str, Any] = None) -> None:
        if proxies is None:
            proxies = {}
        super().__init__("https://api.github.com")
        self.proxies = {proxy_schema + "://": proxy_value for proxy_schema, proxy_value in proxies.items()}
        self.search_base_url = self.base_url + "/search/repositories"
        self.page_bar: Bar
        self.repo_bar: Bar
        self.repo_index = 0

    @sleep_and_retry
    @limits(calls=30, period=60)
    async def request_github(self, url: str) -> Response:
        flag = 0
        while True:
            proxy_dict = self.get_proxy()
            try:
                proxies = {
                    "http://": proxy_dict["http"],
                    "https://": proxy_dict["http"],
                }
                resp = await self.async_request(HttpMethod.GET, url, proxies=proxies)
                if resp.status_code == 403:
                    self.repo_bar.set_description(f"repos{self.repo_index} -> rate_limit: ")
                    await asyncio.sleep(3)
                    continue
                return resp
            except Exception:
                flag += 1
                if flag > 10:
                    self.repo_bar.set_description(f"repos{self.repo_index} -> exception: ")
                    raise

    async def download_readme(self, project_full_name: str, fail_stage: CrawlFailStage, meta_info: Dict[str, Any] = None) -> Tuple[str, str] | None:
        readme_url = f"{self.base_url}/repos/{project_full_name}/readme"
        try:
            response = await self.request_github(readme_url)
            if response.status_code == 200:
                response_data = response.json()
                readme_content = response_data["content"]
                readme_name = response_data["name"]
                decoded_content = base64.b64decode(readme_content).decode("utf-8")
                return decoded_content, readme_name
            raise
        except Exception as e:
            self.repo_bar.set_description(f"repos{self.repo_index} -> failure: ")
            logger.failure(
                json.dumps(
                    {
                        "url": readme_url,
                        "failure_stage": fail_stage.value,
                        "meta_info": meta_info,
                        "error_msg": str(e),
                    }
                )
            )
            return None

    async def handle_request(self, url: str, fail_stage: CrawlFailStage, meta_info: Dict[str, Any] = None) -> Response | None:
        try:
            repo_resp = await self.request_github(url)
            return repo_resp
        except Exception as e:
            logger.failure(
                json.dumps(
                    {
                        "url": url,
                        "failure_stage": fail_stage.value,
                        "meta_info": meta_info,
                        "error_msg": str(e),
                    }
                )
            )
        return None

    @staticmethod
    def get_proxy() -> Dict[str, str]:
        http_proxy = "http://" + config.proxy.proxy
        return {"http": http_proxy}

    async def get_data(self, page_size: int = 100) -> AsyncGenerator[Repositories, None]:  # type: ignore
        total_count = await self.get_total_repo()
        total_page = int(total_count / page_size) + 1
        self.page_bar = tqdm(range(1, total_page + 1), desc="page1: ", total=total_page)
        for page in self.page_bar:
            query_param_str = f"stars:>={self.stars_gte}&sort=stars&per_page={page_size}&page={page}"
            url = self.search_base_url + "?q=" + query_param_str
            repo_resp = await self.handle_request(url, CrawlFailStage.GET_REPOS)
            if repo_resp is None:
                continue
            repos = repo_resp.json()["items"]
            self.repo_bar = tqdm(repos, desc="repos0 -> start: ", total=len(repos))
            for index, repo_json in enumerate(self.repo_bar):
                self.repo_index = index
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
                readme_tuple = await self.download_readme(full_name, CrawlFailStage.GET_README, repo_info)
                if readme_tuple is None:
                    continue
                readme_content, readme_name = readme_tuple
                repo_info["readme_content"] = readme_content
                repo_info["readme_name"] = readme_name
                yield Repositories(**repo_info)
                self.repo_bar.set_description(f"repos{self.repo_index} -> success: ")
                # logger.success(json.dumps(repo_info))
            self.page_bar.set_description(f"page{page}: ")

    async def get_total_repo(self) -> int:
        url = self.search_base_url + "?q=" + f"stars:>={self.stars_gte}"
        resp = await self.request_github(url)
        if resp.status_code == 200:
            data_json = resp.json()
            return data_json["total_count"]
        else:
            raise Exception("Get total_repo failed.")


if __name__ == "__main__":
    proxies = {"https:": "http://localhost:20171"}

    async def run_async_crawl() -> None:
        crawl_github = AsyncCrawlGithub(proxies=proxies)
        async for repo in crawl_github.get_data(page_size=100):
            print(repo)

        # await crawl_github.get_data(page_size=100)

    asyncio.run(run_async_crawl())
