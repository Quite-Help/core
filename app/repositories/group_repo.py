from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import CreateGroupRequest, GroupLinkRequest
from app.schema import Group


def create_group(db: AsyncSession, payload: CreateGroupRequest):
    db.add(
        Group(
            user_alias=payload.user_alias,
            counselor_id=payload.counselor_id,
            user_group_link=payload.user_group_link,
            user_group_id=payload.user_group_id,
            counselor_group_id=payload.counselor_group_id,
            active=True,
        )
    )


async def get_group_by_counselor_and_user_id(
    db: AsyncSession, payload: GroupLinkRequest
) -> Group:
    result = await db.execute(
        select(Group).where(
            Group.counselor_id == payload.counselor_id
            and Group.telegram_user_id == payload.telegram_user_id
        )
    )
    return result.scalar_one_or_none()


async def get_group_by_counselor_group_id(db: AsyncSession, group_id: int) -> Group:
    result = await db.execute(select(Group).where(Group.counselor_group_id == group_id))
    return result.scalar_one_or_none()


async def get_group_by_telegram_user_id(db: AsyncSession, group_id) -> Group:
    result = await db.execute(select(Group).where(Group.user_group_id == group_id))
    return result.scalar_one_or_none()
