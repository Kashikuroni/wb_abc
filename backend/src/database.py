import re
import uuid
from datetime import datetime
from typing import Annotated, Optional
from cryptography.fernet import Fernet

from sqlalchemy import Dialect, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from sqlalchemy.types import VARCHAR, TypeDecorator

from src.config import get_db_url, settings


DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session():
    async with async_session_maker() as session:
        yield session


int_pk = Annotated[int, mapped_column(primary_key=True, unique=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
uuid_pk = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]


class Base(AsyncAttrs, DeclarativeBase):
    """
    Общий базовый класс для всех моделей.

    Автоматически:
        - Генерирует `__tablename__` по имени класса (`snake_case`),
        - Добавляет поля `created_at` и `updated_at` с дефолтами `now()`
    """
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        names = re.split("(?=[A-Z])", cls.__name__)
        return "_".join([x.lower() for x in names if x])

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="Время создания записи",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Время последнего обновления"
    )


fernet = Fernet(settings.SECRET.encode())


class EncryptedString(TypeDecorator[str]):
    """
    Кастомный тип данных для SQLAlchemy, который автоматически шифрует и дешифрует строковые значения.
    Для шифрования используется Fernet из библиотеки cryptography.
    """
    cache_ok = True
    impl = VARCHAR

    def process_bind_param(self, value: Optional[str], dialect: Dialect):
        """
        Метод вызывается при сохранении значения в базу: производится шифрование.
        """
        if value is None:
            return value
        encrypted = fernet.encrypt(value.encode()).decode()
        return encrypted

    def process_result_value(self, value: Optional[str], dialect: Dialect):
        """
        Метод вызывается при извлечении значения из базы: производится дешифрование.
        """
        if value is None:
            return value
        decrypted = fernet.decrypt(value.encode()).decode()
        return decrypted




