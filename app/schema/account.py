import enum
from sqlalchemy import Column, ForeignKey, String, Integer, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(enum.StrEnum):
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SERVICE = "service"


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role = Column(
        ENUM(Role, name="user_role", create_type=True),
        primary_key=True,
    )

    user = relationship("Account", back_populates="role_associations")


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(Text)
    display_name = Column(String)

    role_associations = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    @property
    def roles(self) -> list[Role]:
        return [assoc.role for assoc in self.role_associations]

    def add_role(self, role: Role):
        if role not in self.roles:
            self.role_associations.append(UserRole(role=role))

    def remove_role(self, role: Role):
        self.role_associations = [
            assoc for assoc in self.role_associations if assoc.role != role
        ]
