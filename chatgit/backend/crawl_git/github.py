import asyncio
import json
import random
from enum import Enum
from typing import Any, AsyncGenerator, Dict

from ratelimit import limits, sleep_and_retry  # types: ignore
from requests import Response
from tqdm import tqdm

from chatgit.backend.crawl_git.crawl_git_base import CrawlGitBase, HttpMethod
from chatgit.common import config
from chatgit.common.logger import logger  # types: ignore
from chatgit.models.repositories import Repositories


class CrawlFailStage(str, Enum):
    GET_REPOS = "get_repos"
    GET_CONTENTS = "get_contents"
    GET_README = "get_readme"


class CrawlGithubBase(CrawlGitBase):
    def __init__(self, proxies: Dict[str, Any] = None) -> None:
        if proxies is None:
            proxies = {}
        super().__init__("https://api.github.com/search/repositories")
        self.proxies = proxies


class AsyncCrawlGithub(CrawlGitBase):
    def __init__(self, proxies: Dict[str, Any] = None) -> None:
        if proxies is None:
            proxies = {}
        super().__init__("https://api.github.com/search/repositories")
        self.proxies = {proxy_schema + "://": proxy_value for proxy_schema, proxy_value in proxies.items()}

    @sleep_and_retry
    @limits(calls=30, period=60)
    async def request_github(self, url: str) -> Response:
        flag = 0
        while True:
            proxy_dict = self.get_proxy()
            print(proxy_dict, url)
            try:
                resp = await self.async_request(HttpMethod.GET, url, proxies={"http://": f"http://{proxy_dict['http']}"})
                if resp.status_code == 403:
                    await asyncio.sleep(3)
                    continue
                return resp
            except Exception as e:
                print(e)
                flag += 1
                if flag > 10:
                    raise

    # @sleep_and_retry
    # async def request_content(self, url: str) -> Response:
    #     flag = 0
    #     while True:
    #         proxy_dict = self.get_proxy()
    #         try:
    #             resp = await self.async_request(HttpMethod.GET, url,
    #                                             proxies={"http://": f"http://{proxy_dict['http']}"})
    #             if resp.status_code == 403:
    #                 await asyncio.sleep(3)
    #                 continue
    #             return resp
    #         except Exception:
    #             flag += 1
    #             if flag > 10:
    #                 raise
    #
    #
    #     return await self.async_request(HttpMethod.GET, url, proxies=self.proxies)

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
        proxy_port = random.choice(config.proxy.local_proxy_ports)
        return {"http": f"http://localhost:{proxy_port}"}

    async def get_data(self, page_size: int = 100) -> AsyncGenerator[Repositories, None]:  # type: ignore
        total_count = await self.get_total_repo()
        total_page = int(total_count / page_size) + 1
        for page in tqdm(range(1, total_page + 1), desc="process", total=total_page):
            query_param_str = f"stars:>={self.stars_gte}&sort=stars&per_page={page_size}&page={page}"
            url = self.base_url + "?q=" + query_param_str
            repo_resp = await self.handle_request(url, CrawlFailStage.GET_REPOS)
            if repo_resp is None:
                continue
            repos = repo_resp.json()["items"]
            for repo_json in tqdm(repos, desc="repos", total=len(repos)):
                id = repo_json["id"]
                name = repo_json["name"]
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
                    "index_url": index_url,
                    "api_url": api_url,
                    "description": description,
                    "language": language,
                    "has_wiki": has_wiki,
                    "forks_count": forks_count,
                    "license": license,
                    "topics": topics,
                }
                contents_url = api_url + "/contents"
                contents_resp = await self.handle_request(contents_url, fail_stage=CrawlFailStage.GET_CONTENTS)
                if contents_resp is None:
                    continue
                contents_json = contents_resp.json()
                readme_urls = [file["download_url"] for file in contents_json if file["name"].lower() == "readme.md"]
                if readme_urls:
                    readme_url = readme_urls[0]
                else:
                    logger.failure(
                        json.dumps(
                            {
                                "url": contents_url,
                                "failure_stage": CrawlFailStage.GET_CONTENTS.value,
                                "meta_info": repo_info,
                                "failure_body": contents_resp.json(),
                            }
                        )
                    )
                    continue
                meta_info = repo_info.copy()
                meta_info["readme_url"] = readme_url

                resp = await self.handle_request(readme_url, CrawlFailStage.GET_README, meta_info=repo_info)
                if resp is None:
                    continue
                readme_content = resp.text
                repo_info["readme_content"] = readme_content
                yield Repositories(**repo_info)
                # logger.success(json.dumps(repo_info))

    async def get_total_repo(self) -> int:
        url = self.base_url + "?q=" + f"stars:>={self.stars_gte}"
        resp = await self.request_github(url)
        if resp.status_code == 200:
            data_json = resp.json()
            return data_json["total_count"]
        else:
            raise Exception("Get total_repo failed.")


if __name__ == "__main__":
    proxies = {"https:": "http://localhost:20171"}

    # crawl_github = SyncCrawlGithub(proxies=proxies)
    # crawl_github.get_data(page_size=100)

    async def run_async_crawl() -> None:
        crawl_github = AsyncCrawlGithub(proxies=proxies)
        async for repo in crawl_github.get_data(page_size=100):
            print(repo)

        # await crawl_github.get_data(page_size=100)

    asyncio.run(run_async_crawl())
