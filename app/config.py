"""
Central configuration — reads all sensitive values from environment variables.
Never hardcode secrets here. Set them in a .env file or your cloud secret manager.
"""
import os
import secrets

# ── Security ──────────────────────────────────────────────────────────────────
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
_sk = os.getenv("SECRET_KEY", "")
if not _sk:
    import warnings
    _sk = secrets.token_hex(32)   # random key per-process (dev only)
    warnings.warn(
        "SECRET_KEY not set — a random key was generated. "
        "JWTs will be invalidated on every restart. Set SECRET_KEY in your .env for production.",
        stacklevel=2,
    )

SECRET_KEY = _sk
ALGORITHM  = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES  = int(os.getenv("TOKEN_TTL_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TTL_MINUTES", str(60 * 24 * 7)))  # 7 days

# ── App ───────────────────────────────────────────────────────────────────────
ENV = os.getenv("ENV", "development")      # set ENV=production in prod
DEBUG = ENV != "production"

# ── CORS ─────────────────────────────────────────────────────────────────────
# Comma-separated list of allowed origins, e.g. "https://app.example.com"
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")
