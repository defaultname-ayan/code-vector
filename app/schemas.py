from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductsResponse(BaseModel):
    data: list[ProductOut]
    next_cursor: Optional[str]
    has_more: bool
    total_in_session: int


class NewCountResponse(BaseModel):
    count: int
