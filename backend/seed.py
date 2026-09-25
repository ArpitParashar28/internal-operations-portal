from app.database import Base, engine, SessionLocal
from app.models import User, InventoryItem, Ticket
from app.auth import hash_password

Base.metadata.create_all(engine)
db = SessionLocal()
if not db.query(User).first():
    admin = User(name="Arpit Admin", email="admin@example.com", password_hash=hash_password("password123"), role="admin")
    support = User(name="Mia Support", email="support@example.com", password_hash=hash_password("password123"), role="support")
    employee = User(name="Noah Employee", email="employee@example.com", password_hash=hash_password("password123"), role="employee")
    db.add_all([admin, support, employee]); db.flush()
    db.add_all([
        InventoryItem(sku="LT-001", name="Dell Latitude Laptop", category="IT Equipment", quantity=14, reorder_level=5, location="Berlin Office"),
        InventoryItem(sku="HD-014", name="USB-C Dock", category="IT Equipment", quantity=3, reorder_level=6, location="Berlin Office"),
        InventoryItem(sku="HS-021", name="Jabra Headset", category="Accessories", quantity=8, reorder_level=4, location="Storage A"),
    ])
    db.add_all([
        Ticket(title="VPN access not working", description="Employee cannot connect from home.", priority="high", status="in_progress", requester_id=employee.id, assignee_id=support.id),
        Ticket(title="Replacement laptop required", description="Current device has a battery issue.", priority="medium", status="open", requester_id=employee.id),
        Ticket(title="Payment terminal issue", description="Internal finance terminal shows an error.", priority="critical", status="open", requester_id=employee.id, assignee_id=support.id),
    ])
    db.commit()
print("Seeded. Login: admin@example.com / password123")
