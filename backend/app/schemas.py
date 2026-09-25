from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "employee"

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    active: bool
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ItemCreate(BaseModel):
    sku: str
    name: str
    category: str
    quantity: int = 0
    reorder_level: int = 5
    location: str | None = None

class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    reorder_level: int | None = None
    location: str | None = None
    active: bool | None = None

class ItemOut(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    quantity: int
    reorder_level: int
    location: str | None
    active: bool
    model_config = ConfigDict(from_attributes=True)

class MovementCreate(BaseModel):
    change: int
    reason: str

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"

class TicketUpdate(BaseModel):
    priority: str | None = None
    status: str | None = None
    assignee_id: int | None = None

class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    requester_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
