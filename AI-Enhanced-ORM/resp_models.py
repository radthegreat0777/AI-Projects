from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):

    name: str = Field(..., min_length=3, max_length=255)
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):

    id: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[str] = None

class InvoiceBase(BaseModel):
    user_id: int
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=2, max_length=500)

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AgentQueryRequest(BaseModel):
    query: str
    thread_id: str | None = None

class AgentQueryResponse(BaseModel):
    query: str
    result: str
    thread_id: str

class DMLProposalRequest(BaseModel):
    query: str

class DMLProposalResponse(BaseModel):
    approval_id: str
    sql: str
    status: str


class DMLApprovalRequest(BaseModel):
    approval_id: str
    approve: bool

class DMLApprovalResponse(BaseModel):
    approval_id: str
    status: str
    result: str
