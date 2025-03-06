from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from chatgit.backend.schemas.chat import CompletionRequest
from chatgit.services.chat import ChatService


__all__ = ["router"]

router = APIRouter(prefix="/chat", tags=["qa"])

@router.post("/completions", response_class=EventSourceResponse)
async def completions(schema: CompletionRequest):
    stream = ChatService(schema.model, api_key=schema.api_key, base_url=schema.base_url).chat(repo_url=schema.url.__str__(), github_token=schema.github_token)
    return EventSourceResponse(content=(message.model_dump_json() async for message in stream))