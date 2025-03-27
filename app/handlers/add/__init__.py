from aiogram import Router
from .common import router as common_router
# from .recipe import router as recipes_router
from .ingredient import router as ingredients_router
# from .standalone import router as standalone_router

command_add_router = Router()
command_add_router.include_router(common_router)
# command_add_router.include_router(recipes_router)
command_add_router.include_router(ingredients_router)
# command_add_router.include_router(standalone_router)