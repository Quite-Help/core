from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import check_auth
from app.repositories import counselor_repo
from app.models.counselor import (
    CounselorResponse,
    CounselorInfo,
    CreateCounselorRequest,
)
from app.repositories.base_repo import get_db
from app.schema.account import Role

router = APIRouter(prefix="/counselors", tags=["Counselors"])


@router.get("", response_model=list[CounselorInfo])
async def get_counselors(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(check_auth([Role.ADMIN, Role.SERVICE])),
):
    counselors = await counselor_repo.get_all(db)
    return [
        CounselorInfo(id=c.id, name=f"{c.first_name} {c.last_name}") for c in counselors
    ]


@router.get("/{counselorId}", response_model=CounselorResponse)
async def get_counselor(
    counselorId: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(check_auth([Role.ADMIN, Role.SERVICE])),
):
    c = await counselor_repo.get_by_id(db, counselorId)
    if not c:
        raise HTTPException(404, "Counselor not found")
    return CounselorResponse(
        id=c.id,
        telegram_user_id=c.telegram_id,
        name=f"{c.first_name} {c.last_name}",
        bio=c.bio,
    )


@router.post("")
def create_counselor(
    body: CreateCounselorRequest,
    db=Depends(get_db),
    _=Depends(check_auth([Role.ADMIN])),
):
    counselor_repo.create_counselor(db, body)
