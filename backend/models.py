from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=200)
    parties: str = Field(..., min_length=2, max_length=5000)
    terms: str = Field(..., min_length=2, max_length=10000)
    dates: str = Field(..., min_length=2, max_length=200)


class DocumentResponse(BaseModel):
    success: bool
    document_type: str
    content: str
