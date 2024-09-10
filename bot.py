import asyncio
from aiogram import Bot, Dispatcher

from app.command_add import command_add_router
from app.command_others import command_others_router
from app.command_show import command_show_router
from app.database.models import async_main
from keys import BOT_TOKEN

async def main():
    await async_main()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(command_add_router)
    dp.include_router(command_show_router)
    dp.include_router(command_others_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is stoped")