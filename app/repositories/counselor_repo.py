
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.counselor import CreateCounselorRequest
from app.schema.counselor import Counselor


async def get_all(db: AsyncSession) -> list[Counselor]:
    result = await db.scalars(select(Counselor))
    return result.all()


async def get_by_id(db: AsyncSession, id: int) -> Counselor:
    result = await db.execute(select(Counselor).where(Counselor.id == id))
    return result.scalar_one_or_none()

def create_counselor(db: AsyncSession, payload: CreateCounselorRequest):
    db.add(Counselor(
        first_name=payload.first_name,
        last_name=payload.last_name,
        bio=payload.bio,
        telegram_id=payload.telegram_id
    ))
