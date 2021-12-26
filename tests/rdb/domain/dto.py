from pydantic import BaseModel, Field


class MemoRequest(BaseModel):
    content: str = Field(title="Memo content")
