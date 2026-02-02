from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    user_alias = Column(String)
    counselor_id = Column(Integer, ForeignKey("counselors.id"))
    active = Column(Boolean, default=True)
    user_group_link = Column(String, nullable=True)
    counselor_group_id = Column(Integer)
    user_group_id = Column(Integer)
