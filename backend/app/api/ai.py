from fastapi import APIRouter, HTTPException, status

from app.ai.predictor import predict_category
from app.schemas.ai import (
    TicketCategoryPrediction,
    TicketCategoryRequest,
)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/predict-category",
    response_model=TicketCategoryPrediction,
)
def predict_ticket_category(
    request: TicketCategoryRequest,
) -> TicketCategoryPrediction:
    try:
        result = predict_category(
            title=request.title,
            description=request.description,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model is not available. Train the model first.",
        ) from None

    return TicketCategoryPrediction(**result)
