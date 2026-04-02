"""
Seed script — populates the database with demo users and transactions.
Run once: python seed.py

Users created:
  admin   / admin123   (role: admin)
  analyst / analyst123 (role: analyst)
  viewer  / viewer123  (role: viewer)
"""

import sys
from datetime import date, timedelta
import random

sys.path.insert(0, ".")

from app.database import SessionLocal, engine
from app.models import Base, User, UserRole, Transaction, TransactionType
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Users ───────────────────────────────────────────────────────────────────
USERS = [
    {"username": "admin",   "email": "admin@finance.local",   "password": "admin123",   "role": UserRole.admin},
    {"username": "analyst", "email": "analyst@finance.local", "password": "analyst123", "role": UserRole.analyst},
    {"username": "viewer",  "email": "viewer@finance.local",  "password": "viewer123",  "role": UserRole.viewer},
]

created_users = []
for u in USERS:
    existing = db.query(User).filter(User.username == u["username"]).first()
    if not existing:
        user = User(
            username=u["username"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(user)
        db.flush()
        created_users.append(user)
        print(f"  Created user: {user.username} ({user.role.value})")
    else:
        created_users.append(existing)
        print(f"  User already exists: {existing.username}")

db.commit()

# ── Transactions ─────────────────────────────────────────────────────────────
admin_user = db.query(User).filter(User.username == "admin").first()

INCOME_CATEGORIES  = ["Salary", "Freelance", "Investments", "Rental", "Bonus"]
EXPENSE_CATEGORIES = ["Rent", "Groceries", "Utilities", "Transport", "Dining", "Healthcare", "Entertainment"]

today = date.today()
transactions_added = 0

for i in range(60):
    tx_date  = today - timedelta(days=random.randint(0, 180))
    tx_type  = TransactionType.income if i % 3 == 0 else TransactionType.expense
    category = random.choice(INCOME_CATEGORIES if tx_type == TransactionType.income else EXPENSE_CATEGORIES)

    amount = round(
        random.uniform(5000, 80000) if tx_type == TransactionType.income else random.uniform(500, 15000),
        2,
    )

    tx = Transaction(
        amount   = amount,
        type     = tx_type,
        category = category,
        date     = tx_date,
        notes    = f"Auto-seeded {tx_type.value} record #{i+1}",
        user_id  = admin_user.id,
    )
    db.add(tx)
    transactions_added += 1

db.commit()
db.close()

print(f"\n✅ Seed complete — {transactions_added} transactions added.")
print("\nDemo credentials:")
print("  admin   / admin123")
print("  analyst / analyst123")
print("  viewer  / viewer123")
