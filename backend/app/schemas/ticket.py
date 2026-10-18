
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TicketPriority = Literal["low", "medium", "high", "urgent"]
TicketStatus = Literal[
    "open",
    "in_progress",
    "waiting_for_customer",
    "resolved",
    "closed",
]


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    category: str | None = Field(default=None, max_length=100)
    priority: TicketPriority = "medium"


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str | None
    priority: str
    status: str
    created_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketAssign(BaseModel):
    assigned_to: int = Field(gt=0)


class TicketCommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
