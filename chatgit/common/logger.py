from loguru import logger


logger.add("crawl.log", rotation="500 MB")  # 每当日志文件达到 500MB 时切割
