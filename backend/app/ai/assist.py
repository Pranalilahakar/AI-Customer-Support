import re

from app.models.comment import TicketComment
from app.models.ticket import Ticket


def summarize_ticket(ticket: Ticket, comments: list[TicketComment]) -> dict:
    """Create a concise extractive summary from ticket content."""
    description = re.sub(r"\s+", " ", ticket.description).strip()
    latest_comment = ""

    if comments:
        latest_comment = re.sub(
            r"\s+", " ", comments[-1].body
        ).strip()

    summary_parts = [
        f"Ticket: {ticket.title.strip()}",
        f"Issue: {description[:500]}",
        f"Status: {ticket.status}; Priority: {ticket.priority}",
    ]

    if latest_comment:
        summary_parts.append(f"Latest comment: {latest_comment[:300]}")

    return {
        "ticket_id": ticket.id,
        "summary": " ".join(summary_parts),
        "comment_count": len(comments),
    }


def suggest_reply(ticket: Ticket, comments: list[TicketComment]) -> dict:
    """Return a transparent template-based draft for agent review."""
    latest_comment = ""

    if comments:
        latest_comment = re.sub(
            r"\s+", " ", comments[-1].body
        ).strip()

    draft = (
        f"Hello,\n\n"
        f"Thank you for contacting support about '{ticket.title}'. "
        "We are reviewing the issue and will work with you toward a resolution."
    )

    if latest_comment:
        draft += (
            "\n\nWe have also noted your latest update: "
            f'"{latest_comment[:250]}"'
        )

    draft += (
        "\n\nIf you have any additional details or steps to reproduce the issue, "
        "please share them with us.\n\nBest regards,\nSupport Team"
    )

    return {
        "ticket_id": ticket.id,
        "draft": draft,
        "generated_by": "template",
        "requires_agent_review": True,
    }
