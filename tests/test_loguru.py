from loguru import logger


def my_sink(message):
    record = message.record
    print(record)
    # update_db(message, time=record["time"], level=record["level"])


logger.add("file.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", serialize=lambda x: x["message"])
logger.debug("调试消息")
