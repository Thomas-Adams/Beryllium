"""
Integration tests for Pydantic DTOs.

These verify that:
- DTOs serialize correctly from SQLAlchemy objects
- Nested relationships are resolved
- Excluded fields don't leak
- Create/Update DTOs validate input properly
"""

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Status,  Content,ContentTypes,CmsNodes, Folders, Content, Categories


# Import your DTOs — adjust to match your actual DTO module
from app.dto import (StatusRead, ContentRead, ContentElementsRead, ContentDefinitionRead, ContentDefinitionItemsRead,
                     FoldersRead, ContentTypesRead, ContentTypesCreate, CmsNodesRead, make_read_dto, \
    make_create_dto, StatusCreate)

pytestmark = pytest.mark.dto


# ── Basic DTO serialization ─────────────────────────────

class TestStatusDto:
    async def test_status_serialization(self, session: AsyncSession, seed_statuses):
        """StatusRead should serialize all fields from a SQLAlchemy object."""
        status = await session.scalar(
            select(Status).where(Status.name == "published")
        )
        dto = StatusRead.model_validate(status)

        assert dto.id == status.id
        assert dto.name == "published"
        assert dto.description == "Content is live"

    async def test_status_to_json(self, session: AsyncSession, seed_statuses):
        """Verify JSON serialization round-trip."""
        status = await session.scalar(
            select(Status).where(Status.name == "draft")
        )
        dto = StatusRead.model_validate(status)
        json_data = dto.model_dump()

        assert isinstance(json_data, dict)
        assert json_data["name"] == "draft"
        assert "id" in json_data


# ── Nested relationship DTOs ────────────────────────────

class TestContentTypeDto:
    async def test_content_type_with_nested_status(
        self, session: AsyncSession, seed_content_type
    ):
        """ContentTypesRead should include the nested status object."""
        ct = await session.scalar(
            select(ContentTypes)
            .where(ContentTypes.name == "blog-post")
            .options(selectinload(ContentTypes.status))
        )
        # Skip if your content type doesn't have a status relationship
        # or adjust the DTO accordingly
        dto = ContentTypesRead.model_validate(ct)

        assert dto.slug == "blog-post"
        assert dto.display_name == "Blog Post"
        assert dto.schema_json["required"] == ["title", "body"]

    async def test_content_type_json_schema_preserved(
        self, session: AsyncSession, seed_content_type
    ):
        """The schema_json JSONB field should survive serialization intact."""
        ct = await session.scalar(
            select(ContentTypes).where(ContentTypes.name == "blog-post")
        )
        dto = ContentTypesRead.model_validate(ct)
        json_data = dto.model_dump()

        assert json_data["schema_json"]["type"] == "object"
        assert "title" in json_data["schema_json"]["properties"]
        assert "body" in json_data["schema_json"]["properties"]


# ── Create DTOs (input validation) ──────────────────────

class TestCreateDtos:
    def test_content_type_create_valid(self):
        """A valid payload should pass validation."""
        dto = ContentTypesCreate.model_validate({
            "slug": "landing-page",
            "display_name": "Landing Page",
            "schema_json": {"type": "object", "properties": {}},
            "created_by": "test",
        })
        assert dto.slug == "landing-page"

    def test_content_type_create_missing_required(self):
        """Missing required fields should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ContentTypesCreate.model_validate({
                "slug": "incomplete",
                # missing display_name and schema_json
            })
        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "display_name" in field_names or "schema_json" in field_names

    def test_content_create_valid(self):
        """Content create should accept valid data."""
        dto = ContentTypesCreate.model_validate({
            "content_type_id": 1,
            "title": "My Post",
            "slug": "my-post",
            "data": {"title": "My Post", "body": "<p>Hello</p>"},
            "created_by": "test",
        })
        assert dto.title == "My Post"
        assert dto.data["body"] == "<p>Hello</p>"

    def test_create_dto_excludes_auto_fields(self):
        """Create DTOs should not accept id, version, created_at etc."""
        dto = ContentTypesCreate.model_validate({
            "slug": "test",
            "display_name": "Test",
            "schema_json": {},
            "created_by": "test",
            "id": 999,           # should be ignored or rejected
            "version": 5,        # should be ignored or rejected
        })
        # If extra="forbid" is set, this would raise ValidationError
        # If extra="ignore" (default), the extra fields are silently dropped
        assert not hasattr(dto, "id") or dto.model_fields_set == {"slug", "display_name", "schema_json", "created_by"}


# ── Self-referential DTOs (CmsNodes) ────────────────────

class TestCmsNodeDto:
    async def test_node_with_parent(self, session: AsyncSession, seed_statuses):
        """CmsNodeOut should resolve parent one level deep."""
        parent = CmsNodes(path="root.site", sort_order=0, status_id=1, cms_node_type="folder")
        session.add(parent)
        await session.flush()
        session.add(parent)
        await session.flush()
        session.add(parent)
        await session.flush()

        child = CmsNodes(
            cms_node_type="content",
            parent_id=parent.id,
            path="root.site.page",
            status_id=1,
            sort_order=1,
        )
        session.add(child)
        await session.flush()

        # Load with parent eagerly loaded
        result = await session.scalar(
            select(CmsNodes)
            .where(CmsNodes.id == child.id)
            .options(
                selectinload(CmsNodes.parent),
                selectinload(CmsNodes.children),
            )
        )

        dto = CmsNodesRead.model_validate(result)
        assert dto.node_type == "content"
        assert dto.path == "root.site.page"
        assert dto.parent is not None
        assert dto.parent.path == "root.site"
        assert dto.children == []

    async def test_node_with_children(self, session: AsyncSession, seed_statuses):
        """CmsNodeOut should list children."""
        parent = CmsNodes(cms_node_type="folder", path="root", sort_order=0)
        session.add(parent)
        await session.flush()

        child1 = CmsNodes(
            parent_id=parent.id, cms_node_type="folder",
            path="root.blog", sort_order=1,
        )
        child2 = CmsNodes(
            parent_id=parent.id, cms_node_type="folder",
            path="root.products", sort_order=2,
        )
        session.add_all([child1, child2])
        await session.flush()

        result = await session.scalar(
            select(CmsNodes)
            .where(CmsNodes.id == parent.id)
            .options(selectinload(CmsNodes.children))
        )

        dto = CmsNodesRead.model_validate(result)
        assert len(dto.children) == 2

    async def test_shallow_node_no_recursion(self, session: AsyncSession, seed_statuses):
        """CmsNodeShallow should not include nested parent/children objects."""
        node = CmsNodes(cms_node_type="folder", path="root.flat", sort_order=0)
        session.add(node)
        await session.flush()

        dto = (CmsNodesRead.model_validate(node))
        assert dto.path == "root.flat"
        # Shallow should not have parent/children as nested objects
        assert not hasattr(dto, "parent") or dto.parent is None
        assert not hasattr(dto, "children") or dto.children is None


# ── Full content with relations ─────────────────────────

class TestContentDto:
    async def test_content_with_all_relations(
        self, session: AsyncSession, seed_statuses, seed_content_type
    ):
        """ContentOut should resolve status, category, and content_definition."""
        # Create category
        category = Categories(
            name="Tech", version=1,
        )
        session.add(category)
        await session.flush()

        # Create node + content
        node = CmsNodes(cms_node_type="content", path="root.tech.post", sort_order=0)
        session.add(node)
        await session.flush()

        content = Content(
            title="Python Tips",
            description="Tips for Python developers",
            data={"title": "Python Tips", "body": "<p>Use type hints</p>"},
            category_id=category.id,
            status="published",
            version=1,
            created_by="test",
        )
        session.add(content)
        await session.flush()

        # Load with all relationships
        result = await session.scalar(
            select(Content)
            .where(Content.id == content.id)
            .options(
                selectinload(Content.node),
            )
        )

        dto = ContentRead.model_validate(result)
        assert dto.title == "Python Tips"
        assert dto.data["body"] == "<p>Use type hints</p>"


# ── DTO factory tests (make_read_dto / make_create_dto) ─

class TestDtoFactory:
    def test_make_read_dto_has_from_attributes(self):
        """Generated read DTOs should have from_attributes=True."""
        dto_class = make_read_dto(Status)
        assert dto_class.model_config.get("from_attributes") is True

    def test_make_read_dto_excludes_fks(self):
        """Excluded FK fields should not appear in the DTO."""
        dto_class = make_read_dto(Content, exclude_fks=["status_id", "category_id"])
        field_names = set(dto_class.model_fields.keys())
        assert "status_id" not in field_names
        assert "category_id" not in field_names

    def test_make_read_dto_includes_nested(self):
        """Extra fields (nested relations) should appear in the DTO."""
        dto_class = make_read_dto(
            Content,
            exclude_fks=["status_id"],
            status=StatusRead | None,
        )
        assert "status" in dto_class.model_fields

    def test_make_create_dto_excludes_auto_fields(self):
        """Create DTOs should not include id, version, timestamps."""
        dto_class = make_create_dto(Status)
        field_names = set(dto_class.model_fields.keys())
        assert "id" not in field_names
        assert "version" not in field_names
        assert "created_at" not in field_names
        assert "updated_at" not in field_names

    async def test_read_dto_from_db_object(
        self, session: AsyncSession, seed_statuses
    ):
        """A generated read DTO should convert from a live DB object."""
        status_out = make_read_dto(Status)

        status = await session.scalar(
            select(Status).where(Status.name == "published")
        )
        dto = status_out.model_validate(status)
        assert dto.name == "published"

    async def test_create_dto_round_trip(
        self, session: AsyncSession, seed_statuses
    ):
        """Create DTO → dict → SQLAlchemy object → DB → Read DTO."""
        status_create = make_create_dto(Status)
        status_read = make_read_dto(Status)

        # Simulate API input
        input_data = StatusCreate.model_validate({
            "name": "suspended",
            "description": "Account suspended",
            "created_by": "test",
        })

        # Convert to SQLAlchemy object
        status = Status(
            id=500,
            version=1,
            **input_data.model_dump(),
        )
        session.add(status)
        await session.flush()

        # Read it back and convert to read DTO
        result = await session.get(Status, 500)
        output_data = StatusRead.model_validate(result)

        assert output_data.name == "suspended"
        assert output_data.id == 500
        assert output_data.version == 1
