from chatgit.backend.crawl_git.github import AsyncCrawlGithub
from chatgit.models import database


async def run_async_crawl() -> None:
    if not database.is_connected:
        await database.connect()
    crawl_github = AsyncCrawlGithub(proxies=proxies)
    async for repo in crawl_github.get_data(page_size=100):
        await repo.save()
    await database.disconnect()


if __name__ == "__main__":
    proxies = {"https:": "http://localhost:20171"}
    import asyncio

    asyncio.run(run_async_crawl())
