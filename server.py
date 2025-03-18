from contextlib import asynccontextmanager
import time
from typing import AsyncIterator, Callable

from fastapi import FastAPI, Request, Response

from chatgit.backend.views import app_router
from chatgit.models import base_ormar_config


def get_lifespan(config):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if not config.database.is_connected:
            await config.database.connect()

        yield

        if config.database.is_connected:
            await config.database.disconnect()

    return lifespan


app = FastAPI(docs_url="/api/v1/docs", lifespan=get_lifespan(base_ormar_config))


@app.middleware("http")  # type: ignore
async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Response]
) -> Response:
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.debug = True


app.include_router(app_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        reload=False,
        log_level="debug",
    )
