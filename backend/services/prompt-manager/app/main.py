from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, REGISTRY
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import prompts, schemas, test_suites, audit_logs, admin, billing, invoices, internal
from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import engine
from app.db.base import Base
from app.jobs.secret_rotation import rotation_loop
from app.jobs.audit_retention import retention_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.AUTO_CREATE_TABLES:
        # For development only; in production use Alembic migrations.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    stop_event = asyncio.Event()
    tasks: list[asyncio.Task] = []
    if settings.SECRET_ROTATION_ENABLED:
        tasks.append(asyncio.create_task(rotation_loop(stop_event)))
    if settings.AUDIT_RETENTION_ENABLED:
        tasks.append(asyncio.create_task(retention_loop(stop_event)))
    yield
    # Shutdown
    stop_event.set()
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    await engine.dispose()


app = FastAPI(
    title="Prompt Manager API",
    version="0.1.0",
    lifespan=lifespan,
)

if "prompt_manager_requests_total" in REGISTRY._names_to_collectors:
    REQUEST_COUNTER = REGISTRY._names_to_collectors["prompt_manager_requests_total"]
else:
    REQUEST_COUNTER = Counter(
        "prompt_manager_requests_total",
        "Total prompt-manager API requests",
        ["path", "method"],
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(schemas.router, prefix="/api/v1/schemas", tags=["schemas"])
app.include_router(
    test_suites.router, prefix="/api/v1/test-suites", tags=["test-suites"]
)
app.include_router(
    audit_logs.router, prefix="/api/v1/audit-logs", tags=["audit-logs"]
)
app.include_router(
    admin.router, prefix="/api/v1/admin", tags=["admin"]
)
app.include_router(
    internal.router, prefix="/api/v1/internal", tags=["internal"]
)
app.include_router(
    billing.router, prefix="/api/v1/billing", tags=["billing"]
)
app.include_router(
    invoices.router, prefix="/api/v1/invoices", tags=["invoices"]
)


@app.get("/")
async def root():
    REQUEST_COUNTER.labels("/", "GET").inc()
    return {"message": "Prompt Manager API"}


@app.get("/health")
async def health() -> dict:
    REQUEST_COUNTER.labels("/health", "GET").inc()
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
