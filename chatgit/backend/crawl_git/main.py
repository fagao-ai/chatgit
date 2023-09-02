import logging

from chatgit.backend.crawl_git.github import AsyncCrawlGithub
from chatgit.models import database

logging.basicConfig(level=logging.INFO)


async def run_async_crawl() -> None:
    if not database.is_connected:
        await database.connect()
    crawl_github = AsyncCrawlGithub()
    async for repo in crawl_github.get_data(page_size=100):
        await repo.save()
    await database.disconnect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_async_crawl())
