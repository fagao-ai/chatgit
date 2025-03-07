import time
from typing import Callable

from fastapi import FastAPI, Request, Response

from chatgit.backend.views import app_router

app = FastAPI(docs_url="/api/v1/docs")


@app.middleware("http")  # type: ignore
async def add_process_time_header(request: Request, call_next: Callable[[Request], Response]) -> Response:
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
        reload=True,
        log_level="debug",
    )
