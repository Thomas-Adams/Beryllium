"""
Shared test fixtures for Beryl CMS integration tests.

Requirements:
  - A running PostgreSQL instance (use the Docker Compose: make up)
  - A test database will be created/dropped automatically

Usage:
  pytest                    # run all tests
  pytest -m models          # only model tests
  pytest -m dto             # only DTO tests
  pytest -v                 # verbose output
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import List

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ── Import your models and DTOs ─────────────────────────
# Adjust these imports to match your actual project structure
from app.models.base import Base
from app.models.user import Users
from app.models.status import Status, StatusEnum
from app.models.content import ContentTypes, Content, ContentDefinitions, ContentDefinitionItems, DataTypes, ContentGroups, ContentElementGroups, ContentElements, CmsNodes, DataFields, \
    AllowedChildren, FolderAllowedChildren, Folders, DataTypesEnum
from app.models.media import MediaTypes, MimeTypes, Media, MediaVariant
from app.models.taxonomy import ContentTags, Categories, Tags, MediaTags
# ── Test database config ────────────────────────────────
# Points to the SAME Postgres server as dev, but a DIFFERENT database
TEST_DB_HOST = "localhost"
TEST_DB_PORT = 5432
TEST_DB_USER = "beryl_admin"
TEST_DB_PASS = "beryl_secret"
TEST_DB_NAME = "beryl_test"  # separate from the dev "beryl" database

ADMIN_DB_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
)

TEST_DB_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)


# ── Session-scoped: create/drop the test database once ──
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create the test database, yield an engine connected to it,
    then drop the test database after all tests complete.
    """
    # Connect to the default 'postgres' database to create/drop the test db
    admin_engine = create_async_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")

    async with admin_engine.connect() as conn:
        # Drop if exists from a previous failed run
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME} OWNER {TEST_DB_USER}"))

    await admin_engine.dispose()

    # Create the engine for the test database
    engine = create_async_engine(TEST_DB_URL, echo=False)

    # Enable extensions needed by the schema
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS ltree"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    async with engine.begin() as conn:
        await conn.run_sync("CREATE SCHEMA IF NOT EXISTS main")
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Teardown: drop all tables, then drop the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    # Drop the test database
    admin_engine = create_async_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    await admin_engine.dispose()


@pytest.fixture(scope="session")
async def session_factory(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the test engine."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture()
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional session for each test.
    Rolls back after each test so tests don't pollute each other.
    """
    async with session_factory() as session:
        async with session.begin():
            yield session
            # Rollback after each test — clean slate every time
            await session.rollback()


# ── Reusable seed fixtures ──────────────────────────────

@pytest.fixture()
async def seed_statuses(session: AsyncSession) -> list[Status]:
    """Insert standard statuses and return them."""
    statuses = [
        Status(id=1, name="draft", description="Content is being authored",
               version=1, created_by="test"),
        Status(id=2, name="in_review", description="Awaiting review",
               version=1, created_by="test"),
        Status(id=3, name="published", description="Content is live",
               version=1, created_by="test"),
        Status(id=4, name="archived", description="Content retired",
               version=1, created_by="test"),
        Status(id=5, name="blocked", description="Content is blocked and cannot be edited nor published until unblocked",
               version=1, created_by="test"),
    ]
    session.add_all(statuses)
    await session.flush()
    return statuses


@pytest.fixture()
async def seed_admin_user(session: AsyncSession, seed_statuses) -> Users:
    """Insert an admin user and return it."""
    user = Users(
        email="admin@beryl.local",
        username="Test Admin",
        password_hash="fakehash",
        status_id=StatusEnum.PUBLISHED.value,
        role="beryl_admin",
    )
    session.add(user)
    await session.flush()
    return user


@pytest.fixture()
async def seed_content_type(session: AsyncSession, seed_statuses) -> List[ContentTypes]:

    ct0 = (ContentTypes(
        name="Blog Post",
        description="A standard blog post",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct0)
    await session.flush()

    ct1 = (ContentTypes(
        name="Image Basic",
        description="A standard html page with an article and an image",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct1)
    await session.flush()

    ct2 = (ContentTypes(
        name="Teaser",
        description="A Link with text and image",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct2)
    await session.flush()
    return [ct0,ct1,ct2]




@pytest.fixture()
async def seed_data_types(session: AsyncSession, seed_statuses) -> List[DataTypes]:
    ct_string = (DataTypes(
        name=DataTypesEnum.STRING,
        description="A standard text of one line",
        scala="String",
        typescript="string",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct_string)
    ct_integer = (DataTypes(
        name=DataTypesEnum.INTEGER,
        description="A standard integer number",
        scala="Int",
        typescript="number",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct_integer)
    ct_double = (DataTypes(
        name=DataTypesEnum.DOUBLE,
        description="A standard double number",
        scala="Double",
        typescript="number",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct_double)
    ct_timestamptz = (DataTypes(
        name=DataTypesEnum.TIMESTAMPTZ,
        description="A standard datatime with timezone",
        scala="java.time.OffsetDateTime",
        typescript="Date",
        version=1,
        status_id=StatusEnum.PUBLISHED.value,
        created_by="test",
    ))
    session.add(ct_timestamptz)
    await session.flush()
    return [ct_string,ct_integer,ct_double,ct_timestamptz]

@pytest.fixture()
async def seed_data_fields( session: AsyncSession, seed_statuses, seed_data_types ) -> List[DataFields]:
    df_1 = DataFields(
        name="positive_integer_number",
        description="A required positive integer number",
        datatype_id=DataTypesEnum.INTEGER,
        version=1,
        pattern="^[1-9][0-9]*$",
        required=True,
        status_id=StatusEnum.PUBLISHED.value
    )
    session.add(df_1)
    df_2 = DataFields(
        name="A label",
        description="A required label",
        datatype_id=DataTypesEnum.STRING,
        min_length=2,
        max_length=50,
        version=1,
        status_id=StatusEnum.PUBLISHED.value
    )
    session.add(df_2)
    await session.flush()
    return [df_1,df_2]

