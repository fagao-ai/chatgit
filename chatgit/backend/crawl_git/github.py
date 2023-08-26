import json
from enum import Enum
from typing import Any, AsyncGenerator, Dict, Generator

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


class SyncCrawlGithub(CrawlGithubBase):
    @sleep_and_retry
    @limits(calls=10, period=60)
    def request_github(self, url: str) -> Response:
        return self.sync_request(HttpMethod.GET, url, proxies=self.proxies)

    @sleep_and_retry
    @limits(calls=10, period=60)
    def request_content(self, url: str) -> Response:
        return self.sync_request(HttpMethod.GET, url, proxies=self.proxies)

    def get_data(self, page_size: int = 100) -> Generator[int, None, Repositories]:  # type: ignore
        total_count = self.get_total_repo()
        total_page = int(total_count / page_size) + 1
        for page in tqdm(range(1, total_page + 1), desc="process", total=total_page):
            query_param_str = f"stars:>={self.stars_gte}&sort=stars&per_page={page_size}&page={page}"
            url = self.base_url + "?q=" + query_param_str
            repo_resp = self.request_github(url)
            if repo_resp.status_code != 200:
                logger.failure(
                    json.dumps(
                        {
                            "url": url,
                            "failure_stage": CrawlFailStage.GET_REPOS.value,
                            "meta_info": {},
                            "failure_body": repo_resp.json(),
                        }
                    )
                )
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
                contents_resp = self.request_github(contents_url)
                if contents_resp.status_code != 200:
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
                # readme_url = [file['html_url'] for file in contents_json if file['name'].lower() == 'readme.md'][0]
                resp = self.request_content(readme_url)
                if resp.status_code != 200:
                    logger.failure(
                        json.dumps(
                            {
                                "url": readme_url,
                                "failure_stage": CrawlFailStage.GET_README.value,
                                "meta_info": repo_info,
                            }
                        )
                    )
                    continue
                readme_content = resp.text
                repo_info["readme_content"] = readme_content
                # logger.success(json.dumps(repo_info))
                yield Repositories(**repo_info)
            # print(readme_content)

    def get_total_repo(self) -> int:
        url = self.base_url + "?q=" + f"stars:>={self.stars_gte}"
        resp = self.request_github(url)
        if resp.status_code == 200:
            data_json = resp.json()
            return data_json["total_count"]
        else:
            raise Exception("Get total_repo failed.")


class AsyncCrawlGithub(CrawlGitBase):
    def __init__(self, proxies: Dict[str, Any] = None) -> None:
        if proxies is None:
            proxies = {}
        super().__init__("https://api.github.com/search/repositories")
        self.proxies = {proxy_schema + "://": proxy_value for proxy_schema, proxy_value in proxies.items()}

    @sleep_and_retry
    # @limits(calls=10, period=60)
    async def request_github(self, url: str) -> Response:
        proxy_dict = self.get_proxy()
        return await self.async_request(HttpMethod.GET, url, proxies={"http://": f"http://{proxy_dict['http']}"})

    @sleep_and_retry
    @limits(calls=10, period=60)
    async def request_content(self, url: str) -> Response:
        return await self.async_request(HttpMethod.GET, url, proxies=self.proxies)

    @staticmethod
    def get_proxy() -> Dict[str, str]:
        import requests

        proxy_json = requests.get(config.proxy.github_api_proxy_pool)
        proxy = proxy_json.json()["proxy"]
        print("proxy_json: ", proxy)
        return {"http": proxy}

    async def get_data(self, page_size: int = 100) -> AsyncGenerator[Repositories, Repositories]:  # type: ignore
        total_count = await self.get_total_repo()
        total_page = int(total_count / page_size) + 1
        for page in tqdm(range(1, total_page + 1), desc="process", total=total_page):
            query_param_str = f"stars:>={self.stars_gte}&sort=stars&per_page={page_size}&page={page}"
            url = self.base_url + "?q=" + query_param_str
            repo_resp = await self.request_github(url)
            if repo_resp.status_code != 200:
                logger.failure(
                    json.dumps(
                        {
                            "url": url,
                            "failure_stage": CrawlFailStage.GET_REPOS.value,
                            "meta_info": {},
                            "failure_body": repo_resp.json(),
                        }
                    )
                )
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
                contents_resp = await self.request_github(contents_url)
                if contents_resp.status_code != 200:
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
                contents_json = contents_resp.json()
                readme_urls = [file["download_url"] for file in contents_json if file["name"].lower() == "readme.md"]
                if readme_urls:
                    readme_url = readme_urls[0]
                    # print(readme_url)
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
                # readme_url = [file['html_url'] for file in contents_json if file['name'].lower() == 'readme.md'][0]
                resp = await self.request_content(readme_url)
                if resp.status_code != 200:
                    logger.failure(
                        json.dumps(
                            {
                                "url": readme_url,
                                "failure_stage": CrawlFailStage.GET_README.value,
                                "meta_info": repo_info,
                            }
                        )
                    )
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
    import asyncio

    async def run_async_crawl() -> None:
        crawl_github = AsyncCrawlGithub(proxies=proxies)
        async for repo in crawl_github.get_data(page_size=100):
            print(repo)

        # await crawl_github.get_data(page_size=100)

    asyncio.run(run_async_crawl())
