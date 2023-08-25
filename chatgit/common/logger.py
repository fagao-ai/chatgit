from loguru import logger

from chatgit.common.common import CRAWL_DATA

# logger.add("crawl.log", rotation="500 MB")  # 每当日志文件达到 500MB 时切割
logger.add(
    sink=CRAWL_DATA / "crawl-success.jsonlines",
    # format=lambda message: json.dumps(message),
    format="{message}",
    enqueue=True,
    rotation="500 MB",
    encoding="utf-8",
    filter=lambda record: "SUCCESS" in record["level"].name,
)

logger.add(
    sink=CRAWL_DATA / "crawl-failure.log",
    format="{message}",
    # format=lambda message: json.dumps(message),
    enqueue=True,
    rotation="500 MB",
    encoding="utf-8",
    filter=lambda record: "FAILURE" in record["level"].name,
)

logger.level(name="FAILURE", no=35)
logger.failure = lambda *args, **kwargs: logger.opt(depth=1).log("FAILURE", *args, **kwargs)  # type: ignore
