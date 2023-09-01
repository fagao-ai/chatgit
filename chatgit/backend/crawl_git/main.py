from chatgit.backend.crawl_git.github import AsyncCrawlGithub
from chatgit.models import database


async def run_async_crawl() -> None:
    if not database.is_connected:
        await database.connect()
    crawl_github = AsyncCrawlGithub()
    find_proxies_task = crawl_github.find_proxies()
    background_find_proxies = asyncio.create_task(find_proxies_task)
    async for repo in crawl_github.get_data(page_size=100):
        await repo.save()
    await database.disconnect()
    background_find_proxies.cancel()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_async_crawl())
