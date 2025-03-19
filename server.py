from contextlib import asynccontextmanager
import time
from typing import Any, AsyncIterator, Awaitable, Callable
from ormar import OrmarConfig

from fastapi import FastAPI, Request, Response

from chatgit.backend.views import app_router
from chatgit.common.config import DB_ENABLE
from chatgit.models import base_ormar_config


def get_lifespan(config: OrmarConfig):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if DB_ENABLE and not config.database.is_connected:
            await config.database.connect()

        yield

        if DB_ENABLE and config.database.is_connected:
            await config.database.disconnect()

    return lifespan


app = FastAPI(docs_url="/api/v1/docs", lifespan=get_lifespan(base_ormar_config))


@app.middleware("http")  # type: ignore
async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.debug = True


app.include_router(app_router)


if __name__ == "__main__":
    # import uvicorn

    # uvicorn.run(
    #     "server:app",
    #     host="0.0.0.0",
    #     reload=False,
    #     log_level="debug",
    # )
    import asyncio
    from granian import loops, Granian  # type: ignore
    from granian.constants import Interfaces
    from pathlib import Path

    current_dir = Path(__file__).resolve().parent

    @loops.register("auto")
    def build_loop():
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        return asyncio.new_event_loop()

    async def with_connect(function: Callable[..., Awaitable[Any]]):
        # note that for any other backend than sqlite you actually need to
        # connect to the database to perform db operations

        async with base_ormar_config.database:
            await function()

    # org = Organization(org_id=1, name="sube", meta={"test": "test"})
    # asyncio.new_event_loop().run_until_complete(with_connect(org.save))
    Granian(
        f"{__name__}:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=False,
    ).serve()
