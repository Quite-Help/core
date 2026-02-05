from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Counselor(Base):
    __tablename__ = "counselors"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    bio = Column(Text)
    telegram_id = Column(Integer)
