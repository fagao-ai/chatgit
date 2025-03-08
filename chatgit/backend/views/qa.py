from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from chatgit.backend.schemas.chat import CompletionRequest
from chatgit.services.chat import ChatService


__all__ = ["router"]

router = APIRouter(prefix="/chat", tags=["qa"])


@router.post("/completions", response_class=EventSourceResponse)
async def completions(schema: CompletionRequest):
    stream = ChatService(
        schema.model, api_key=schema.api_key, base_url=schema.base_url
    ).chat(repo_url=schema.url.__str__(), github_token=schema.github_token)
    return EventSourceResponse(
        content=(message.model_dump_json() async for message in stream)
    )
    import json
    async def aa():
        md = """# chatgit

```python
import uvicorn
from invoke import task
from invoke.context import Context


@task
def clean(ctx: Context):
    ctx.run("rm -rf dist/* build/*")
    ctx.run('find . -type d -name "__pycache__" -exec rm -r {} +')


@task(aliases=["s"])
def server(_: Context):
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
    )

```

### 哈哈
        """
        for i in md:
            yield json.dumps({"content": i})
    return EventSourceResponse(content=aa())


@router.get("/health")
async def health():
    return {"status": "ok", "user_name": "sube"}
