from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .models import User, InventoryItem, StockMovement, Ticket
from .schemas import *
from .auth import hash_password, verify_password, create_token, current_user, require_roles

Base.metadata.create_all(engine)
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.cors_origins], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if data.role not in {"employee", "support", "manager", "admin"}:
        raise HTTPException(400, "Invalid role")
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already exists")
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return TokenOut(access_token=create_token(user.id, user.role))

@app.get("/users", response_model=list[UserOut])
def users(_: User = Depends(require_roles("manager", "admin")), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.name)).all()

@app.get("/inventory", response_model=list[ItemOut])
def inventory(low_stock: bool = False, _: User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(InventoryItem).where(InventoryItem.active == True).order_by(InventoryItem.name)
    if low_stock:
        q = q.where(InventoryItem.quantity <= InventoryItem.reorder_level)
    return db.scalars(q).all()

@app.post("/inventory", response_model=ItemOut, status_code=201)
def create_item(data: ItemCreate, _: User = Depends(require_roles("manager", "admin")), db: Session = Depends(get_db)):
    if data.quantity < 0:
        raise HTTPException(400, "Quantity cannot be negative")
    item = InventoryItem(**data.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "SKU already exists")
    db.refresh(item)
    return item

@app.patch("/inventory/{item_id}", response_model=ItemOut)
def update_item(item_id: int, data: ItemUpdate, _: User = Depends(require_roles("manager", "admin")), db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit(); db.refresh(item); return item

@app.post("/inventory/{item_id}/movement", response_model=ItemOut)
def stock_movement(item_id: int, data: MovementCreate, user: User = Depends(require_roles("support", "manager", "admin")), db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    new_qty = item.quantity + data.change
    if new_qty < 0:
        raise HTTPException(409, "Stock cannot go below zero")
    item.quantity = new_qty
    db.add(StockMovement(item_id=item.id, change=data.change, reason=data.reason, created_by=user.id))
    db.commit(); db.refresh(item); return item

@app.delete("/inventory/{item_id}", status_code=204)
def delete_item(item_id: int, _: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    item.active = False
    db.commit()

@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(data: TicketCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.priority not in {"low", "medium", "high", "critical"}:
        raise HTTPException(400, "Invalid priority")
    ticket = Ticket(**data.model_dump(), requester_id=user.id)
    db.add(ticket); db.commit(); db.refresh(ticket); return ticket

@app.get("/tickets", response_model=list[TicketOut])
def tickets(status: str | None = None, priority: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(Ticket).order_by(Ticket.updated_at.desc())
    if user.role == "employee":
        q = q.where(Ticket.requester_id == user.id)
    if status:
        q = q.where(Ticket.status == status)
    if priority:
        q = q.where(Ticket.priority == priority)
    return db.scalars(q).all()

@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, data: TicketUpdate, _: User = Depends(require_roles("support", "manager", "admin")), db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    values = data.model_dump(exclude_unset=True)
    if "status" in values and values["status"] not in {"open", "in_progress", "resolved", "closed"}:
        raise HTTPException(400, "Invalid status")
    if "priority" in values and values["priority"] not in {"low", "medium", "high", "critical"}:
        raise HTTPException(400, "Invalid priority")
    for k, v in values.items():
        setattr(ticket, k, v)
    db.commit(); db.refresh(ticket); return ticket

@app.get("/dashboard")
def dashboard(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return {
        "inventory_items": db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.active == True)),
        "low_stock_items": db.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.active == True, InventoryItem.quantity <= InventoryItem.reorder_level)),
        "open_tickets": db.scalar(select(func.count(Ticket.id)).where(Ticket.status.in_(["open", "in_progress"]))),
        "critical_tickets": db.scalar(select(func.count(Ticket.id)).where(Ticket.priority == "critical", Ticket.status != "closed")),
    }
