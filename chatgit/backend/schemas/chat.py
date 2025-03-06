from pydantic import BaseModel, Field, HttpUrl

class CompletionRequest(BaseModel):
    url: HttpUrl
    model: str
    api_key: str | None = Field(default=None)
    base_url: str | None = Field(default=None)
    github_token: str | None = Field(default=None)
