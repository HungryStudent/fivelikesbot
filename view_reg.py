import asyncio
from aiogram_broadcaster import TextBroadcaster
from utils.db import get_not_view, get_new_reg
from create_bot import bot
from keyboards import my_estimates, premium


async def main():
    data = await get_not_view()
    for user in data:
        try:
            await bot.send_message(user["user_id"], "<i>У вас есть новые непросмотренные оценки</i>🙈",
                                   reply_markup=my_estimates,
                                   parse_mode="HTML")
        except Exception as e:
            print(e)
    data = await get_new_reg()
    for user in data:
        try:

            await bot.send_message(user["user_id"], """<b>{name}! Вы с нами уже 2 дня</b>♥️
        
Самое время попробовать Premium режим🌪

<b>Преимущества Premium</b>👇🏻

🔥 Больше оценок (x10)
💌 Отправление сообщений
🔙 Перемотка назад  
⛔️ Не тревожат рекламные рассылки""".format(name=user["name"]), reply_markup=premium,
                                   parse_mode="HTML")
        except Exception as e:
            print(e)


asyncio.run(main())
