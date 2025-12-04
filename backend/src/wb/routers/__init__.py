from fastapi import APIRouter, Depends
from src.dependencies import auth

from .orders import router as orders_router

wb_router = APIRouter(
    prefix="/wb",
    dependencies=[Depends(auth.access_token_required)]
)

wb_router.include_router(orders_router)

