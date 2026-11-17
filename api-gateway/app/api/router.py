from fastapi import APIRouter
from .routers.auth import router as auth_router
from .routers.orders import router as orders_router
from .routers.catalog import router as catalog_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(orders_router)
router.include_router(catalog_router)
