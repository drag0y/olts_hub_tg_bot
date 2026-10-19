import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from routes.user_private import u_router
from routes.route_olts import olts_router
from common.cmds_list import private

load_dotenv()


bot = Bot(
    token=os.getenv('TG_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
dp = Dispatcher()

dp.include_router(olts_router)
dp.include_router(u_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())