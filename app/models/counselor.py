from pydantic import BaseModel


class CounselorInfo(BaseModel):
    id: int
    name: str


class CounselorResponse(BaseModel):
    id: int
    telegram_user_id: int
    name: str
    bio: str

class CreateCounselorRequest(BaseModel):
    first_name: str
    last_name: str
    bio: str
    telegram_id: int
