from pydantic import BaseModel, ConfigDict


class AliasResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    alias: str


class AliasRequest(BaseModel):
    telegram_user_id: str
