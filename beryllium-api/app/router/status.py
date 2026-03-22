from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, add_pagination, paginate
from app.database.database import get_session

from app.models.status import Status
from app.dto import StatusRead
from app.utils.pagination import paginate_query

router = APIRouter(prefix="/api/status", tags=["Status"])


async def list_status(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Status).order_by(Status.name))
    status_list = []
    for r in result: status_list.append(StatusRead.model_validate(r))
    return status_list


@router.get("", response_model=Page[StatusRead])
async def get_status_page(
        name: str | None = None,
        created_by: str | None = None,
        search: str | None = None,
        session: AsyncSession = Depends(get_session)) -> Page[StatusRead]:
    query = select(Status).order_by(Status.name)
    if name:
        query = query.where(Status.name == name)

    if created_by:
        query = query.where(Status.created_by == created_by)

    if search:
        query = query.where(Status.name.ilike(f"%{search}%"))

    return await paginate_query(session, query,StatusRead)
