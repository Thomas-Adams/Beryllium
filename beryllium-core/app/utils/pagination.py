from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as _paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


async def paginate_query(
    session: AsyncSession,
    query: Select,
    dto_class: type,
):
    """Paginate a SQLAlchemy query and convert results to a DTO."""
    return await _paginate(
        session,
        query,
        transformer=lambda items: [
            dto_class.model_validate(item) for item in items
        ],
    )