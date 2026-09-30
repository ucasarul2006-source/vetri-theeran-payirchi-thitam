from fastapi import APIRouter, HTTPException

from backend.models import DocumentRequest, DocumentResponse
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
_generator = None


def get_generator() -> GeminiDocumentGenerator:
    global _generator

    if _generator is None:
        _generator = GeminiDocumentGenerator()

    return _generator


@router.post("/generate", response_model=DocumentResponse)
def generate_document(payload: DocumentRequest):
    try:
        content = get_generator().generate_document(
            document_type=payload.document_type,
            parties=payload.parties,
            terms=payload.terms,
            dates=payload.dates,
        )

        return DocumentResponse(
            success=True,
            document_type=payload.document_type,
            content=content,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
