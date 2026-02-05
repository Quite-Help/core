from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.core.security import check_auth
from app.models.group import (
    CreateGroupRequest,
    GroupLinkRequest,
    ResolveGroupRequest,
    ResolveGroupResponse,
    GroupLinkResponse,
)
from app.repositories import counselor_repo, group_repo
from app.repositories.base_repo import get_db
from app.schema.account import Role

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("")
def create_group(
    payload: CreateGroupRequest,
    _: dict = Depends(check_auth([Role.SERVICE])),
    db=Depends(get_db),
):
    group_repo.create_group(db, payload)


@router.post("/resolve", response_model=ResolveGroupResponse)
async def resolve_group(
    payload: ResolveGroupRequest,
    _: dict = Depends(check_auth([Role.SERVICE])),
    db=Depends(get_db),
):
    user_group = await group_repo.get_group_by_telegram_user_id(db, payload.group_id)
    if user_group is not None:
        return ResolveGroupResponse(
            target_group_id=user_group.counselor_group_id,
            display_name=user_group.user_alias,
        )
    counselor_group = await group_repo.get_group_by_counselor_group_id(
        db, payload.group_id
    )
    if counselor_group is not None:
        counselor = await counselor_repo.get_by_id(counselor_group.counselor_id)
        return ResolveGroupResponse(
            target_group_id=counselor_group.user_group_id,
            display_name=f"{counselor.firstName} {counselor.lastName}",
        )
    raise HTTPException(404, "group not found")


@router.post("/link", response_model=GroupLinkResponse)
async def get_group_link(
    payload: GroupLinkRequest,
    _: dict = Depends(check_auth([Role.SERVICE])),
    db=Depends(get_db),
):
    group = await group_repo.get_group_by_counselor_and_user_id(db, payload)
    if not group:
        raise HTTPException(404, "group not found")
    return GroupLinkResponse(group_link=group.user_group_link)
