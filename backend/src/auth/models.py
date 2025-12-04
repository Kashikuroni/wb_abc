import enum

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ENUM as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, uuid_pk


class Role(enum.Enum):
    ADMIN = "admin"
    WAREHOUSE = "warehouse"
    ANALYTIC = "analytic"
    CONTENT = "content"
    GUEST = "guest"


class User(Base):
    __table_args__ = {"schema": "auth"}
    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(48), nullable=False)
    last_name: Mapped[str] = mapped_column(String(48), nullable=False)
    username: Mapped[str] = mapped_column(String(48), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    hashed_password: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        comment="Password hash (bcrypt/argon2)",
    )
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="user_roles", schema="auth", create_type=False),
        default=Role.GUEST,
        nullable=False,
    )
