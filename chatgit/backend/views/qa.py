from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from chatgit.backend.schemas.chat import CompletionRequest, GithubRequest
from chatgit.services.chat import ChatService
from chatgit.services.github import Github


__all__ = ["router"]

router = APIRouter(prefix="/chat", tags=["qa"])


@router.post("/git-repo", response_class=EventSourceResponse)
async def chat_git_repo(schema: GithubRequest):
    stream = ChatService(
        api_key=schema.api_key,
        base_url=schema.base_url,
        model=schema.model,
    ).repo_chat(repo_url=schema.url.__str__(), github_token=schema.github_token)
    return EventSourceResponse(
        content=(item.model_dump_json() async for item in stream)
    )


@router.post("/completions")
async def completions(schema: CompletionRequest):
    repo, onwer = Github.parse_github_url(schema.messages[0].content)
    schema.messages[0].content = """
    You are a helpful assistant that answers questions about a GitHub repository.
    The repository is {repo} owned by {owner}.
    Please answer my question based on the conversation history and answer the question with Simplified Chinese.
    """.format(repo=repo, owner=onwer)
    stream = ChatService(
        api_key=schema.api_key,
        base_url=schema.base_url,
        model=schema.model,
    ).chat(schema.messages)
    return EventSourceResponse(
        content=(item.model_dump_json() async for item in stream)
    )


@router.post("/title")
async def generate_title(schema: CompletionRequest):
    _, repo = Github.parse_github_url(schema.messages[0].content)
    return {
        "title": await ChatService(
            model=schema.model,
            api_key=schema.api_key,
            base_url=schema.base_url,
        ).get_title(repo, schema.messages),
    }
