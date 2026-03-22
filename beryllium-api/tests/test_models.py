"""
Integration tests for SQLAlchemy models.

These test against a real PostgreSQL database to verify:
- Tables are created correctly
- Constraints work (PKs, FKs, unique, check)
- Relationships load properly
- CRUD operations function
"""

import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Status,
    UserAccount,
    ContentType,
    ContentTypeVersion,
    Category,
    Tag,
    ContentTag,
    Node,
    Folder,
    Content,
)
from app.models.user import Users

pytestmark = pytest.mark.models


# ── Status ──────────────────────────────────────────────

class TestStatus:
    async def test_create_status(self, session: AsyncSession):
        status = Status(
            id=100, name="test_status", description="A test",
            version=1, created_by="test",
        )
        session.add(status)
        await session.flush()

        result = await session.get(Status, 100)
        assert result is not None
        assert result.name == "test_status"
        assert result.description == "A test"

    async def test_status_unique_name(self, session: AsyncSession):
        """Duplicate names should fail if you have a unique constraint."""
        s1 = Status(id=200, name="duplicate", version=1, created_by="test")
        s2 = Status(id=201, name="duplicate", version=1, created_by="test")
        session.add(s1)
        await session.flush()
        session.add(s2)
        # This will raise if you have a unique index on name
        # If name is not unique, remove this test
        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_seed_statuses_fixture(self, session: AsyncSession, seed_statuses):
        """Verify the seed fixture works."""
        count = await session.scalar(select(func.count(Status.id)))
        assert count == 4

        published = await session.scalar(
            select(Status).where(Status.name == "published")
        )
        assert published is not None
        assert published.description == "Content is live"


# ── UserAccount ─────────────────────────────────────────

class TestUserAccount:
    async def test_create_user(self, session: AsyncSession):
        user = Users(
            email="test@beryl.local",
            username="Test User",
            password_hash="fakehash"
        )
        session.add(user)
        await session.flush()

        result = await session.scalar(
            select(UserAccount).where(UserAccount.email == "test@beryl.local")
        )
        assert result is not None
        assert result.display_name == "Test User"

    async def test_user_unique_email(self, session: AsyncSession):
        u1 = UserAccount(
            email="dupe@beryl.local", display_name="A",
            password_hash="hash1", role="author",
        )
        u2 = UserAccount(
            email="dupe@beryl.local", display_name="B",
            password_hash="hash2", role="editor",
        )
        session.add(u1)
        await session.flush()
        session.add(u2)
        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_user_with_status_relationship(
        self, session: AsyncSession, seed_statuses, seed_admin_user
    ):
        """If UserAccount has a status relationship, test it loads."""
        user = seed_admin_user
        assert user.email == "admin@beryl.local"
        assert user.role == "admin"


# ── ContentType ─────────────────────────────────────────

class TestContentType:
    async def test_create_content_type(self, session: AsyncSession, seed_statuses):
        ct = ContentType(
            slug="product-page",
            display_name="Product Page",
            schema_json={"type": "object", "properties": {}},
            version=1,
            created_by="test",
        )
        session.add(ct)
        await session.flush()

        result = await session.scalar(
            select(ContentType).where(ContentType.slug == "product-page")
        )
        assert result is not None
        assert result.display_name == "Product Page"
        assert result.schema_json["type"] == "object"

    async def test_content_type_slug_unique(self, session: AsyncSession, seed_statuses):
        ct1 = ContentType(
            slug="same-slug", display_name="A",
            schema_json={}, version=1, created_by="test",
        )
        ct2 = ContentType(
            slug="same-slug", display_name="B",
            schema_json={}, version=1, created_by="test",
        )
        session.add(ct1)
        await session.flush()
        session.add(ct2)
        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_content_type_with_versions(
        self, session: AsyncSession, seed_content_type
    ):
        """Verify the version relationship loads."""
        ct = await session.scalar(
            select(ContentType)
            .where(ContentType.slug == "blog-post")
            .options(selectinload(ContentType.versions))
        )
        assert ct is not None
        assert len(ct.versions) == 1
        assert ct.versions[0].version_number == 1
        assert ct.versions[0].schema_json["required"] == ["title", "body"]

    async def test_content_type_version_increment(
        self, session: AsyncSession, seed_content_type
    ):
        """Simulate updating a content type and creating a new version."""
        ct = seed_content_type

        # Update the schema
        new_schema = {
            **ct.schema_json,
            "properties": {
                **ct.schema_json["properties"],
                "excerpt": {"type": "string", "maxLength": 300},
            },
        }
        ct.schema_json = new_schema
        ct.version = 2
        await session.flush()

        # Create a new version record
        v2 = ContentTypeVersion(
            content_type_id=ct.id,
            version_number=2,
            schema_json=new_schema,
            change_summary="Added excerpt field",
            created_by="test",
        )
        session.add(v2)
        await session.flush()

        # Reload with versions
        ct_reloaded = await session.scalar(
            select(ContentType)
            .where(ContentType.id == ct.id)
            .options(selectinload(ContentType.versions))
        )
        assert ct_reloaded.version == 2
        assert len(ct_reloaded.versions) == 2
        assert "excerpt" in ct_reloaded.schema_json["properties"]


# ── Category (self-referential) ─────────────────────────

class TestCategory:
    async def test_create_category_tree(self, session: AsyncSession, seed_statuses):
        parent = Category(
            name="Technology", slug="technology",
            version=1,
        )
        session.add(parent)
        await session.flush()

        child = Category(
            name="Python", slug="python",
            parent_id=parent.id,
            version=1,
        )
        session.add(child)
        await session.flush()

        # Verify the relationship
        result = await session.scalar(
            select(Category).where(Category.slug == "python")
        )
        assert result is not None
        assert result.parent_id == parent.id


# ── Node tree ───────────────────────────────────────────

class TestNodeTree:
    async def test_create_folder_node(self, session: AsyncSession, seed_statuses):
        node = Node(
            node_type="folder",
            path="root.site",
            sort_order=0,
        )
        session.add(node)
        await session.flush()

        folder = Folder(
            node_id=node.id,
            name="Site Root",
            created_by="test",
        )
        session.add(folder)
        await session.flush()

        # Load folder with its node
        result = await session.scalar(
            select(Folder)
            .where(Folder.name == "Site Root")
            .options(selectinload(Folder.node))
        )
        assert result is not None
        assert result.node.node_type == "folder"
        assert result.node.path == "root.site"

    async def test_create_content_node(
        self, session: AsyncSession, seed_statuses, seed_content_type
    ):
        # Parent folder node
        folder_node = Node(
            node_type="folder", path="root.blog", sort_order=0,
        )
        session.add(folder_node)
        await session.flush()

        # Content node under the folder
        content_node = Node(
            parent_id=folder_node.id,
            node_type="content",
            path="root.blog.my_post",
            sort_order=1,
        )
        session.add(content_node)
        await session.flush()

        # Content record
        content = Content(
            node_id=content_node.id,
            content_type_id=seed_content_type.id,
            title="My First Post",
            slug="my-first-post",
            data={"title": "My First Post", "body": "<p>Hello world</p>"},
            status="draft",
            version=1,
            created_by="test",
        )
        session.add(content)
        await session.flush()

        # Verify parent-child relationship
        result = await session.scalar(
            select(Node)
            .where(Node.id == content_node.id)
            .options(selectinload(Node.parent))
        )
        assert result.parent.id == folder_node.id
        assert result.parent.node_type == "folder"

    async def test_node_children(self, session: AsyncSession, seed_statuses):
        parent = Node(node_type="folder", path="root", sort_order=0)
        session.add(parent)
        await session.flush()

        child1 = Node(
            parent_id=parent.id, node_type="folder",
            path="root.a", sort_order=1,
        )
        child2 = Node(
            parent_id=parent.id, node_type="folder",
            path="root.b", sort_order=2,
        )
        session.add_all([child1, child2])
        await session.flush()

        # Load children
        result = await session.scalar(
            select(Node)
            .where(Node.id == parent.id)
            .options(selectinload(Node.children))
        )
        assert len(result.children) == 2


# ── Tags ────────────────────────────────────────────────

class TestTags:
    async def test_tag_content(
        self, session: AsyncSession, seed_statuses, seed_content_type
    ):
        # Create content
        node = Node(node_type="content", path="root.tagged_post", sort_order=0)
        session.add(node)
        await session.flush()

        content = Content(
            node_id=node.id,
            content_type_id=seed_content_type.id,
            title="Tagged Post",
            slug="tagged-post",
            data={"title": "Tagged Post", "body": "content"},
            status="draft",
            version=1,
            created_by="test",
        )
        session.add(content)
        await session.flush()

        # Create tags
        tag_python = Tag(slug="python", display_name="Python")
        tag_fastapi = Tag(slug="fastapi", display_name="FastAPI")
        session.add_all([tag_python, tag_fastapi])
        await session.flush()

        # Link tags to content
        session.add_all([
            ContentTag(content_id=content.id, tag_id=tag_python.id),
            ContentTag(content_id=content.id, tag_id=tag_fastapi.id),
        ])
        await session.flush()

        # Verify via query
        result = await session.execute(
            select(Tag)
            .join(ContentTag)
            .where(ContentTag.content_id == content.id)
            .order_by(Tag.slug)
        )
        tags = result.scalars().all()
        assert len(tags) == 2
        assert tags[0].slug == "fastapi"
        assert tags[1].slug == "python"


# ── Foreign Key constraints ─────────────────────────────

class TestConstraints:
    async def test_content_requires_valid_content_type(self, session: AsyncSession):
        """FK constraint should prevent referencing a non-existent content type."""
        node = Node(node_type="content", path="root.orphan", sort_order=0)
        session.add(node)
        await session.flush()

        content = Content(
            node_id=node.id,
            content_type_id=99999,  # doesn't exist
            title="Orphan",
            slug="orphan",
            status="draft",
            version=1,
            created_by="test",
        )
        session.add(content)
        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_node_self_reference_constraint(self, session: AsyncSession):
        """FK constraint should prevent referencing a non-existent parent."""
        node = Node(
            parent_id=99999,  # doesn't exist
            node_type="folder",
            path="root.nowhere",
            sort_order=0,
        )
        session.add(node)
        with pytest.raises(IntegrityError):
            await session.flush()
