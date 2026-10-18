from fastapi import HTTPException
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.auth import UserResponse
from app.schemas.ticket import TicketAssign
from app.core.dependencies import require_role
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
)
from app.models.comment import TicketComment
from app.schemas.ticket import (
    TicketAssign,
    TicketCommentCreate,
    TicketCommentResponse,
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

def get_accessible_ticket(
    ticket_id: int,
    current_user: User,
    db: Session,
) -> Ticket:
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    if current_user.role == "admin":
        return ticket

    if (
        current_user.role == "customer"
        and ticket.created_by == current_user.id
    ):
        return ticket

    if (
        current_user.role == "agent"
        and ticket.assigned_to == current_user.id
    ):
        return ticket

    raise HTTPException(
        status_code=403,
        detail="You do not have access to this ticket.",
    )

@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_ticket = Ticket(
        title=ticket_data.title.strip(),
        description=ticket_data.description.strip(),
        category=ticket_data.category,
        priority=ticket_data.priority,
        created_by=current_user.id,
    )

    try:
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
    except Exception:
        db.rollback()
        raise

    return new_ticket


@router.get("/my-tickets", response_model=list[TicketResponse])
def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = (
        select(Ticket)
        .where(Ticket.created_by == current_user.id)
        .order_by(Ticket.created_at.desc())
    )

    return db.scalars(statement).all()

@router.get("/assigned-to-me", response_model=list[TicketResponse])
def get_assigned_tickets(
    current_user: User = Depends(require_role("agent")),
    db: Session = Depends(get_db),
):
    statement = (
        select(Ticket)
        .where(Ticket.assigned_to == current_user.id)
        .order_by(Ticket.created_at.desc())
    )
    return db.scalars(statement).all()

@router.get(
    "/admin/all",
    response_model=list[TicketResponse],
)
def get_all_tickets_for_admin(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Return all customer tickets to administrators only."""
    statement = select(Ticket).order_by(Ticket.created_at.desc())

    return db.scalars(statement).all()


@router.get(
    "/agents",
    response_model=list[UserResponse],
)
def get_active_agents(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Return active agents for the admin assignment interface."""
    statement = (
        select(User)
        .where(
            User.role == "agent",
            User.is_active.is_(True),
        )
        .order_by(User.full_name.asc())
    )

    return db.scalars(statement).all()

@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    assignment: TicketAssign,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    agent = db.get(User, assignment.assigned_to)

    if agent is None or not agent.is_active:
        raise HTTPException(status_code=404, detail="Active agent not found.")

    if agent.role != "agent":
        raise HTTPException(
            status_code=422,
            detail="Tickets can only be assigned to agents.",
        )

    ticket.assigned_to = agent.id

    try:
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise

    return ticket

@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("admin", "agent"):
        raise HTTPException(
            status_code=403,
            detail="Only admins and agents can update ticket status.",
        )

    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    if (
        current_user.role == "agent"
        and ticket.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only update tickets assigned to you.",
        )

    ticket.status = status_data.status

    try:
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise

    return ticket

@router.post(
    "/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_comment(
    ticket_id: int,
    comment_data: TicketCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_accessible_ticket(ticket_id, current_user, db)

    new_comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        body=comment_data.body.strip(),
    )

    if not new_comment.body:
        raise HTTPException(
            status_code=422,
            detail="Comment cannot be empty.",
        )

    try:
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
    except Exception:
        db.rollback()
        raise

    return new_comment


@router.get(
    "/{ticket_id}/comments",
    response_model=list[TicketCommentResponse],
)
def get_ticket_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_accessible_ticket(ticket_id, current_user, db)

    statement = (
        select(TicketComment)
        .where(TicketComment.ticket_id == ticket_id)
        .order_by(TicketComment.created_at.asc(), TicketComment.id.asc())
    )

    return db.scalars(statement).all()