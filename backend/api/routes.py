import logging

from fastapi import APIRouter, HTTPException

from backend.api.schemas import QueryRequest, QueryResponse
from backend.curve.generator import run_curve_generation
from backend.curve.models import GenerateCurveRequest, GenerateCurveResponse
from backend.rag.pipeline import run_rag_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
def ask(request: QueryRequest) -> QueryResponse:
    try:
        result = run_rag_pipeline(request.query, top_k=request.top_k)
        return QueryResponse(**result)
    except Exception:
        logger.exception("RAG pipeline failed for query: %s", request.query)
        raise HTTPException(status_code=500, detail="Failed to process query.")


@router.post("/generate-curve", response_model=GenerateCurveResponse)
def generate_curve(request: GenerateCurveRequest) -> GenerateCurveResponse:
    try:
        return run_curve_generation(request)
    except Exception:
        logger.exception("Curve generation failed for request: %s", request)
        raise HTTPException(status_code=500, detail="Failed to generate curve.")
