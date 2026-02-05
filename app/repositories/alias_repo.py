from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema import Alias


async def get_by_telegram_user_id(db: AsyncSession, telegram_user_id: str) -> Alias:
    result = await db.scalars(
        select(Alias).where(Alias.telegram_user_id == telegram_user_id)
    )
    return result.all()


def create_user_alias(db: AsyncSession, telegram_user_id: str, alias: str):
    db.add(Alias(telegram_user_id=telegram_user_id, alias=alias))
