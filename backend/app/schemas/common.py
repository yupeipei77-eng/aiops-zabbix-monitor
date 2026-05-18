from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = ""


class PaginatedResponse(BaseModel):
    success: bool = True
    data: list = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    message: str = ""


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
