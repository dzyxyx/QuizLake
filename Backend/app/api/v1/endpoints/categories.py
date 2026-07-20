from fastapi import APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Category
from app.schemas.category import CategoryRead

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
async def get_categories(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Category))
    category = result.scalars().all()

    return category