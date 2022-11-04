from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram_broadcaster import TextBroadcaster
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from create_bot import dp, bot
from config import admin_chat
from handlers.texts import *
from states.admin import *
import keyboards as kb
from utils import db


@dp.message_handler(state="*", text="Отменить", chat_id=admin_chat)
async def cancel_input(message: Message, state: FSMContext):
    await message.answer("Ввод остановлен", reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.callback_query_handler(Text(startswith="ban_"), chat_id=admin_chat)
async def ban_user(call: CallbackQuery):
    data = call.data.split("_")
    await db.change_ban(int(data[1]), True)
    await call.message.answer(f"Пользователь <code>{data[1]}</code> заблокирован", parse_mode="HTML")
    reporter_data = await db.get_user(int(data[2]))
    await call.bot.send_message(data[2], accept_ban_reporter_text.format(name=reporter_data["name"]))
    await call.bot.send_message(data[1], accept_ban_user_text, reply_markup=kb.ask_amnesty)
    await call.message.delete()


@dp.callback_query_handler(Text(startswith="unban_"), chat_id=admin_chat)
async def amnesty_unban(call: CallbackQuery):
    user_id = call.data[6:]
    await db.change_ban(int(user_id), False)
    await call.message.answer(f"Пользователь <code>{user_id}</code> разблокирован", parse_mode="HTML")
    await call.bot.send_message(user_id, "Ваш аккаунт разблокирован!")
    await call.message.delete()


@dp.callback_query_handler(text="admin_dismiss_report", chat_id=admin_chat)
async def dismiss_ban_user(call: CallbackQuery):
    await call.message.answer(f"Жалоба на пользователя отклонена", parse_mode="HTML")
    await call.message.delete()


@dp.callback_query_handler(text="admin_dismiss_amnesty", chat_id=admin_chat)
async def dismiss_unban_user(call: CallbackQuery):
    await call.message.answer(f"Амнистия пользователя отклонена", parse_mode="HTML")
    await call.message.delete()


@dp.message_handler(commands="unban", chat_id=admin_chat)
async def unban_user(message: Message):
    user_id = message.get_args()
    if user_id == "":
        await message.answer("Введите id пользователя после /unban. Пример: /unban 1234")
        return
    await db.change_ban(int(user_id), False)
    await message.answer("Пользователь разблокирован")


@dp.message_handler(commands="premium", chat_id=admin_chat)
async def gift_premium(message: Message):
    try:
        user_id, days = message.get_args().split()
    except ValueError:
        await message.answer("Введите id пользователя и кол-во дней. Пример: /premium 1234 1")
        return
    await db.add_premium(int(user_id), int(days))
    await message.answer("Premium выдан")
    await message.bot.send_message(user_id, f"Администратор подключил вам премиум, дней {days}")


@dp.message_handler(commands="stat", chat_id=admin_chat)
async def show_stat(message: Message):
    data = await db.get_stat()
    await message.answer(f"""Всего пользователей: {data['all_count']}
За сегодня: {data['today_count']}

Оценённых анкет всего: {data["all_likes_count"]}
За сегодня: {data["today_likes_count"]}

Подключено Premium всего: {data["all_premium"]}
За сегодня: {data["today_premium"]}
Активных: {data["active_premium"]}""")


@dp.message_handler(commands="send", chat_id=admin_chat)
async def send_text(message: Message):
    await message.answer("Введите текст рассылки", reply_markup=kb.admin_cancel)
    await SendStates.enter_text.set()


@dp.message_handler(state=SendStates.enter_text)
async def start_send(message: Message, state: FSMContext):
    users = await db.get_users()
    broadcaster = TextBroadcaster(users, message.text, bot=bot)
    await message.answer("Начал рассылку", reply_markup=ReplyKeyboardRemove())
    await broadcaster.run()
    await state.finish()


@dp.message_handler(commands="public")
async def change_public(message: Message):
    try:
        group_id, username = message.get_args().split()
    except ValueError:
        await message.answer("Введите id канала и username после /public. Пример: /public 1234 @username")
        return
    with open("partner.txt", "w") as f:
        f.write(f"{group_id} {username}")
    await message.answer("Канал изменен")
