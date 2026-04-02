from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base
from .routers import auth, transactions, analytics, users, export

STATIC_DIR = Path(__file__).parent / "static"

# ── Create all tables on startup ────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Finance Tracker API",
    description = (
        "A Python-based finance tracking system supporting CRUD operations "
        "on financial records, analytics, and role-based access control.\n\n"
        "**Roles:**\n"
        "- `viewer` — view records and summary\n"
        "- `analyst` — view + filter + detailed analytics\n"
        "- `admin` — full access including create/update/delete and user management\n\n"
        "**Getting Started:** Register via `/auth/register`, login via `/auth/login`, "
        "then use the returned JWT in the `Authorization: Bearer <token>` header."
    ),
    version     = "1.0.0",
    contact     = {"name": "Mukesh Kumar"},
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ─────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(export.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """Serve the custom API landing page."""
    return (STATIC_DIR / "index.html").read_text()
