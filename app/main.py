from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from .database import engine
from .models import Base
from .routers import auth, transactions, analytics, users, export

# Create all tables on startup
Base.metadata.create_all(bind=engine)

# App
# docs_url/redoc_url set to None — custom routes below use unpkg.com instead
# of cdn.jsdelivr.net which is blocked on many networks (causes blank white page).
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
    version  = "1.0.0",
    contact  = {"name": "Mukesh Kumar"},
    docs_url = None,
    redoc_url= None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(export.router)


# Docs routes (CDN-independent)
@app.get("/", include_in_schema=False)
def root():
    return {
        "name": "Finance Tracker API",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc"
    }

@app.get("/docs", include_in_schema=False)
def swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Finance Tracker API — Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
def redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Finance Tracker API — ReDoc",
        redoc_js_url="https://unpkg.com/redoc@latest/bundles/redoc.standalone.js",
    )
