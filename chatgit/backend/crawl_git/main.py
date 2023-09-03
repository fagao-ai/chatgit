import asyncio
import logging
import signal

from chatgit.backend.crawl_git.github import AsyncCrawlGithub
from chatgit.models import database

logging.basicConfig(level=logging.INFO)


async def run_async_crawl() -> None:
    if not database.is_connected:
        await database.connect()
    crawl_github = AsyncCrawlGithub()
    loop = asyncio.get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, crawl_github.stop_crawl)
        # add_signal_handler() is not implemented on Win
        # https://docs.python.org/3.5/library/asyncio-eventloops.html#windows
    except NotImplementedError:
        pass
    async for repo in crawl_github.get_data(page_size=100):
        await repo.save()
    await database.disconnect()


if __name__ == "__main__":
    # https://github.com/constverum/ProxyBroker/issues/162
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_async_crawl())
