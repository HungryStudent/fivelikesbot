import asyncio

from utils.db import get_ending_premium
from create_bot import bot
from keyboards import premium


async def main():
    data = await get_ending_premium()
    for user in data:
        await bot.send_message(user["user_id"], """<b>Name, у вас заканчивается Premium!</b>

<b><i>Для продления выберите подходящий вариант:</i></b>""".format(name=user["name"]), reply_markup=premium,
                               parse_mode="HTML")


asyncio.run(main())
