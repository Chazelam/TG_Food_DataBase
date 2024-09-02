import asyncio
from aiogram import Bot, Dispatcher

from app.command_add import command_add_router
from app.database.models import async_main


async def main():
    await async_main()
    BOT_TOKEN = '944480396:AAGrA-f-MqZOtkBKokEjMVgTm9qnzf5L-AY'
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(command_add_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is stoped")