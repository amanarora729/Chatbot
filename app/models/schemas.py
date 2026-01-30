from pydantic import BaseModel, HttpUrl

class CrawlRequest(BaseModel):
    url: HttpUrl

class CrawlResponse(BaseModel):
    message: str
    chunks_count: int

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
