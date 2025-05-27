from fastapi import APIRouter

from . import barrels, bottler, carts, catalog, admin, info, inventory

router = APIRouter()
router.include_router(barrels.router)
router.include_router(bottler.router)
router.include_router(carts.router)
router.include_router(catalog.router)
router.include_router(admin.router)
# router.include_router(auth.router)
router.include_router(info.router)
router.include_router(inventory.router)
