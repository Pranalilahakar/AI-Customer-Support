from typing import Literal

from pydantic import BaseModel, Field


TicketCategory = Literal[
    "technical_issue",
    "billing",
    "account_access",
    "general_inquiry",
]


class TicketCategoryRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)


class TicketCategoryPrediction(BaseModel):
    category: TicketCategory
    confidence: float = Field(ge=0.0, le=1.0)
