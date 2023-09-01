from typing import Dict

from chatgit.backend.crawl_git.github import AsyncCrawlGithub
from chatgit.models import database


async def run_async_crawl(proxies: Dict[str, str]) -> None:
    if not database.is_connected:
        await database.connect()
    crawl_github = AsyncCrawlGithub(proxies=proxies)
    find_proxies_task = crawl_github.find_proxies()
    background_find_proxies = asyncio.create_task(find_proxies_task)
    async for repo in crawl_github.get_data(page_size=100):
        await repo.save()
    await database.disconnect()
    background_find_proxies.cancel()


if __name__ == "__main__":
    proxies = {"https": "http://172.30.80.1:10809"}
    # proxies = {"http:": "http://39.173.102.18:80"}
    # proxies = {"https:": "http://123.126.158.50:80"}
    # import requests
    #
    # proxy = AsyncCrawlGithub.get_proxy()
    # print(proxy)
    # #
    # # # resp  = requests.get("http://github.com", proxies=proxies)
    # resp  = requests.get("https://ipinfo.io/ip", proxies=proxy)
    # print(resp.text)
    import asyncio

    asyncio.run(run_async_crawl(proxies))
