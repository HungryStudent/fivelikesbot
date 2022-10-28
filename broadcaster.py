import asyncio

from aiogram import Bot
from config import TOKEN
from utils.db import get_users, sql_start

from aiogram_broadcaster import TextBroadcaster

bot = Bot(token=TOKEN)


async def notify_admins(users):
    await TextBroadcaster(users, 'Бот восстановлен, можно пользоваться🥳!', bot=bot).run()


sql_start()
tuple_users = get_users()
users = [x[0] for x in tuple_users]
print(users)
print(len(users))
# asyncio.run(notify_admins(users))
