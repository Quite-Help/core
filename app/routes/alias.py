from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import check_auth
from app.repositories.base_repo import get_db
from app.schema.account import Role
from app.repositories import alias_repo
from app.models.alias import AliasRequest, AliasResponse
from app.util.helper import generate_alias

router = APIRouter(prefix="/aliases", tags=["Aliases"])


@router.post("", response_model=AliasResponse)
async def create_or_get_alias(
    payload: AliasRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(check_auth([Role.SERVICE])),
):
    exisiting_alias = await alias_repo.get_by_telegram_user_id(
        db, payload.telegram_user_id
    )
    if exisiting_alias is not None:
        return AliasResponse(alias=exisiting_alias)
    new_alias = generate_alias()
    alias_repo.create_user_alias(payload.telegram_user_id, new_alias)
    return AliasResponse(alias=new_alias)
