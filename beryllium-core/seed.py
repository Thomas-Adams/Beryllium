import logging

from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.status import Status
from app.models.user import Users

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SEED_STATUSES = [
    {"name": "draft", "description": "Content is being authored"},
    {"name": "in_review", "description": "Content is awaiting editorial review"},
    {"name": "published", "description": "Content is live and visible to the public"},
    {"name": "archived", "description": "Content has been retired from public view"},
]

SEED_ADMIN = {
    "email": "admin@beryl.local",
    "display_name": "Beryl Admin",
    "password": "admin",  # Only for local dev!
    "role": "admin",
}




async def seed_statuses(session: AsyncSession) -> None:
    count = await session.scalar(select(func.count(Status.id)))
    if count and count > 0:
        logger.info(f"Status table already has {count} records, skipping seed")
        return

    for s in SEED_STATUSES:
        session.add(Status(**s, version=1, created_by="system"))
    await session.flush()
    logger.info(f"Seeded {len(SEED_STATUSES)} statuses")


async def seed_admin_user(session: AsyncSession) -> None:
    existing = await session.scalar(
        select(Users).where(Users.email == SEED_ADMIN["email"])
    )
    if existing:
        logger.info(f"Admin user '{SEED_ADMIN['email']}' already exists, skipping")
        return

    user = Users(
        email=SEED_ADMIN["email"],
        username=SEED_ADMIN["display_name"],
        password_hash=pwd_context.hash(SEED_ADMIN["password"]),
        role=SEED_ADMIN["role"],
    )
    session.add(user)
    await session.flush()
    logger.info(f"Seeded admin user: {SEED_ADMIN['email']}")





async def run_seed(session: AsyncSession) -> None:
    """Run all seed operations."""
    logger.info("Running database seed...")
    await seed_statuses(session)
    await seed_admin_user(session)
    await session.commit()
    logger.info("Database seed complete")
