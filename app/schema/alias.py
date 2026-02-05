from sqlalchemy import Column, String
from app.core.database import Base


class Alias(Base):
    __tablename__ = "alias"
    telegram_user_id = Column(String, primary_key=True)
    alias = Column(String)
