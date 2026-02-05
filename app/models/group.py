from pydantic import BaseModel


class ResolveGroupResponse(BaseModel):
    target_group_id: int
    display_name: str


class GroupLinkResponse(BaseModel):
    group_link: str | None = None


class ResolveGroupRequest(BaseModel):
    group_id: int


class CreateGroupRequest(BaseModel):
    user_alias: str
    user_group_link: str
    user_group_id: int
    counselor_id: int
    counselor_group_id: int


class GroupLinkRequest(BaseModel):
    telegram_user_id: str
    counselor_id: int
