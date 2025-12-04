from typing import Annotated

from authx import AuthX, TokenPayload
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.config import authx_config
from src.database import get_async_session


auth = AuthX(config=authx_config, model=User)


DBSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
AuthDep = Annotated[TokenPayload, Depends(auth.access_token_required)]
RefreshDep = Annotated[TokenPayload, Depends(auth.refresh_token_required)]
