from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]
