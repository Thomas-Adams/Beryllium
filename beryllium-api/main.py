import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.database import async_session_factory
from app.router import status
from app.router.status import get_status_page, list_status
from seed import run_seed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name}...")
    async with async_session_factory() as session:
        await run_seed(session)
    logger.info("Startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular dev
        "http://localhost:5173",  # SvelteKit dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(status.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}
