from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.knowledge import search_knowledge
from app.ai.priority import recommend_priority
from app.ai.assist import summarize_ticket, suggest_reply
from app.ai.predictor import predict_category
from app.api.tickets import get_accessible_ticket
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.comment import TicketComment
from app.models.user import User
from app.schemas.ai import (
    TicketCategoryPrediction,
    TicketCategoryRequest,
)

router = APIRouter(prefix="/ai", tags=["AI"])


def _get_ordered_comments(
    ticket_id: int,
    db: Session,
) -> list[TicketComment]:
    statement = (
        select(TicketComment)
        .where(TicketComment.ticket_id == ticket_id)
        .order_by(TicketComment.created_at.asc(), TicketComment.id.asc())
    )
    return list(db.scalars(statement).all())


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


@router.get("/tickets/{ticket_id}/summary")
def get_ticket_summary(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ticket = get_accessible_ticket(ticket_id, current_user, db)
    comments = _get_ordered_comments(ticket_id, db)
    return summarize_ticket(ticket, comments)


@router.get("/tickets/{ticket_id}/suggest-reply")
def get_ticket_reply_suggestion(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ticket = get_accessible_ticket(ticket_id, current_user, db)

    if current_user.role not in ("agent", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents and admins can request reply suggestions.",
        )

    comments = _get_ordered_comments(ticket_id, db)
    return suggest_reply(ticket, comments)
@router.get("/knowledge-search")
def search_support_knowledge(
    q: str = Query(..., min_length=1, max_length=300),
    limit: int = Query(default=3, ge=1, le=5),
    current_user: User = Depends(get_current_user),
) -> dict:
    return search_knowledge(q, limit)
@router.get("/tickets/{ticket_id}/priority-recommendation")
def get_ticket_priority_recommendation(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ticket = get_accessible_ticket(ticket_id, current_user, db)

    return recommend_priority(
        title=ticket.title,
        description=ticket.description,
    )
