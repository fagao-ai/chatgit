from pydantic import BaseModel, Field, HttpUrl

class ChatBase(BaseModel):
    model: str | None = Field(default=None)
    api_key: str | None = Field(default=None)
    base_url: str | None = Field(default=None)
    github_token: str | None = Field(default=None)
class GithubRequest(ChatBase):
    url: HttpUrl


class Message(BaseModel):
    role: str
    content: str

class CompletionRequest(ChatBase):
    messages: list[Message]
