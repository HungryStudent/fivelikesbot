from aiogram.types import Message, CallbackQuery, Update, ChatMember
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.utils.exceptions import ChatNotFound
from aiogram.dispatcher.filters import Text

from config import admin_chat, yoomoney_id, partner_chat, partner_url
from create_bot import dp, bot
from datetime import datetime
from yoomoney import Quickpay
from handlers.texts import *
from states.user import *
from urllib import parse
import keyboards as kb
from utils import db
import asyncio
import time
import re


class CheckRegMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: Update, data: dict):
        if update.message:
            user_id = update.message.from_user.id
            await db.add_action(user_id)
        else:
            return
        curr_state = await dp.storage.get_state(chat=user_id, user=user_id)
        if curr_state == RegStates.enter_name.state or curr_state == RegStates.enter_photo.state or curr_state == ChangeStates.change_photo.state or '/start' in update.message.text or update.message.chat.id == admin_chat:
            return
        try:
            status: ChatMember = await bot.get_chat_member(partner_chat, user_id)
            if status.status == "left":
                await bot.send_message(user_id, no_partner_text, reply_markup=kb.get_partner(partner_url))
                raise CancelHandler()
        except ChatNotFound as e:
            print(e)
            await bot.send_message(admin_chat, "Проблема с каналом партнером")
        if not await db.check_user(user_id):
            raise CancelHandler()


def check_name(name: str):
    if len(name.split()) > 2:
        return True
    if name in bad_words:
        return True
    return not bool(re.search('[а-яА-Я]', name))


async def check_ban(user_id, message: Message):
    data = await db.check_user(user_id)
    if data["is_ban"]:
        await message.answer(error_ban_text)
        raise Exception("User is banned")


async def check_last_referal(user_id):
    count = await db.get_referals_count(user_id)
    if count % 10 == 0:
        await db.add_premium(user_id, 1)
        await bot.send_message(user_id, add_premium_free_text)


async def send_report(reporter_id, user_id, text):
    await db.add_new_estimate(reporter_id, int(user_id), "skip")
    data = await db.get_user(int(user_id))
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await bot.send_photo(admin_chat, data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}

Жалоба: {text}""", reply_markup=kb.admin_report(user_id, reporter_id))


async def show_me_estimate(message: Message, user_id):
    data, count, score = await db.get_estimate_user(user_id)
    if data is None:
        await message.answer("Все оценки уже просмотрены")
        return
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await message.answer_photo(data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}
Оценил(-а) вас на {score}/5""", reply_markup=kb.me_estimates(count, data["user_id"]))


@dp.message_handler(commands='start')
async def start_message(message: Message, state: FSMContext):
    if await db.check_user(message.from_user.id):
        await message.answer(check_menu_text, reply_markup=kb.menu_kb)
    else:
        await RegStates.enter_name.set()
        ref_id = message.get_args()
        if ref_id not in ['', str(message.from_user.id)]:
            await state.update_data(ref_id=ref_id)
        await message.answer(hello_text)


@dp.message_handler(state="*", text="Отмена")
async def cancel_input(message: Message, state: FSMContext):
    await message.answer("Ввод остановлен", reply_markup=kb.menu_kb)
    await state.finish()


@dp.message_handler(state=RegStates.enter_name)
async def enter_gender(message: Message, state: FSMContext):
    if check_name(message.text):
        await message.answer("Пожалуйста, введите корректные данные!")
        return
    await message.answer("Выберите пол", reply_markup=kb.gender)

    await state.update_data(name=message.text)
    await RegStates.next()


@dp.callback_query_handler(Text(startswith="gender"), state=RegStates.enter_gender)
async def enter_photo(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(enter_photo_text.format(name=data["name"]))
    await state.update_data(gender=call.data[7:])
    await RegStates.next()


@dp.message_handler(state=RegStates.enter_photo, content_types='photo')
async def add_user(message: Message, state: FSMContext):
    gender = {"m": "М", "f": "Ж"}
    data = await state.get_data()
    try:
        ref_id = int(data["ref_id"])
    except KeyError:
        ref_id = 0
    await db.add_user(message.from_user.id, data["name"], gender[data["gender"]], message.photo[-1].file_id, ref_id)
    if ref_id != 0:
        await check_last_referal(ref_id)
    await state.finish()
    await message.answer(finish_reg_text)
    await message.answer_chat_action("typing")
    await asyncio.sleep(2)
    await message.answer(check_menu_text, reply_markup=kb.menu_kb)


@dp.message_handler(text="Кто меня оценил❓")
async def me_estimates(message: Message):
    await check_ban(message.from_user.id, message)
    await show_me_estimate(message, message.from_user.id)


@dp.callback_query_handler(text="me_estimate")
async def me_estimate(call: CallbackQuery):
    await check_ban(call.from_user.id, call.message)
    await show_me_estimate(call.message, call.from_user.id)
    await call.answer()


@dp.callback_query_handler(text="next_estimate")
async def next_estimate(call: CallbackQuery):
    await show_me_estimate(call.message, call.from_user.id)
    await call.answer()


@dp.message_handler(text="Поддержка / О боте 💬")
async def show_help(message: Message):
    await message.answer(help_text, parse_mode="HTML")


@dp.message_handler(text="🏆 TOP")
async def show_top(message: Message):
    await message.answer(all_top_text, reply_markup=await kb.get_top("all"))


@dp.callback_query_handler(Text(startswith="top_"))
async def call_show_top(call: CallbackQuery):
    top_time = call.data[4:]
    if top_time == "all":
        await call.message.edit_text(all_top_text, reply_markup=await kb.get_top("all"))
    else:
        await call.message.edit_text(today_top_text, reply_markup=await kb.get_top("today"))


@dp.message_handler(text="👤 Мой профиль")
async def my_profile(message: Message):
    my_info_data = await db.get_my_user(message.from_user.id)
    rating_data = await db.get_user_rating(message.from_user.id)
    age = my_info_data["age"]
    if my_info_data["age"] == 0:
        age = "не указано"
    if my_info_data["premium_time"] > time.time():
        now_day = datetime.today()
        premium_day = datetime.utcfromtimestamp(my_info_data["premium_time"])
        premium_status = f"Активен, осталось дней - {(premium_day - now_day).days + 1}"
    else:
        premium_status = "Неактивен"
    keyboard = kb.active_profile
    if my_info_data["is_deactivate"]:
        keyboard = kb.deactive_profile

    await message.answer_photo(my_info_data["photo_id"], caption=f"""
✨ Имя: {my_info_data["name"]}
👫 Пол: {my_info_data["gender"]}
🔞 Возраст: {age}
🏙 Город: {my_info_data["city"]}
🌟 Ваш рейтинг: {round(my_info_data["rating"], 1)}
⚡️Вас оценили человек: {rating_data["users_count"]}
🔝 Ваша позиция: {my_info_data["rating_pos"]}
🎗 Premium: {premium_status}""", reply_markup=keyboard)


@dp.callback_query_handler(kb.change_data.filter())
async def change(call: CallbackQuery, callback_data: dict):
    change_type = callback_data["type"]
    if change_type == "name":
        await call.message.answer("Введите имя", reply_markup=kb.cancel)
        await ChangeStates.change_name.set()
    if change_type == "city":
        await call.message.answer("Введите город", reply_markup=kb.cancel)
        await ChangeStates.change_city.set()
    if change_type == "gender":
        await call.message.answer("Выберите пол", reply_markup=kb.gender)
    if change_type == "age":
        await call.message.answer("Введите возраст", reply_markup=kb.cancel)
        await ChangeStates.change_age.set()
    if change_type == "photo":
        await call.message.answer("Пришлите фото", reply_markup=kb.cancel)
        await ChangeStates.change_photo.set()
    await call.answer()


@dp.callback_query_handler(Text(startswith="gender"))
async def change_gender(call: CallbackQuery, state: FSMContext):
    gender = {"m": "М", "f": "Ж"}
    await db.change(call.from_user.id, "gender", gender[call.data[7:]])
    await call.message.edit_text("👫 Пол изменен")
    await state.finish()


@dp.message_handler(state=ChangeStates.change_photo, content_types="photo")
async def change_photo(message: Message, state: FSMContext):
    await db.change(message.from_user.id, "photo_id", message.photo[-1].file_id)
    await message.answer("📸 Фото изменено", reply_markup=kb.menu_kb)
    await state.finish()


@dp.message_handler(state=ChangeStates.change_name)
async def change_name(message: Message, state: FSMContext):
    if check_name(message.text):
        await message.answer("Пожалуйста, введите корректные данные!")
        return
    await db.change(message.from_user.id, "name", message.text.title())
    await message.answer("✨ Имя изменено", reply_markup=kb.menu_kb)
    await state.finish()


@dp.message_handler(state=ChangeStates.change_city)
async def change_city(message: Message, state: FSMContext):
    if check_name(message.text):
        await message.answer("Пожалуйста, введите корректные данные!")
        return
    await db.change(message.from_user.id, "city", message.text)
    await message.answer("🏙 Город изменен", reply_markup=kb.menu_kb)
    await state.finish()


@dp.message_handler(state=ChangeStates.change_age)
async def change_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
    except ValueError:
        await message.answer("Укажите ваш реальный возраст!")
        return
    if 0 < age < 9:
        await db.change(message.from_user.id, "age", age)
        await message.answer("🔞 Возраст изменен", reply_markup=kb.menu_kb)
        await state.finish()
    else:
        await message.answer("Укажите ваш реальный возраст!")
        return


@dp.callback_query_handler(text="deactivate")
async def deactivate_profile(call: CallbackQuery):
    await call.message.answer(deactivate_profile_text, reply_markup=kb.accept_deactivate)
    await call.answer()


@dp.callback_query_handler(Text(startswith="deactivate"))
async def finish_deactivate(call: CallbackQuery):
    if call.data[11:] == "accept":
        await db.deactivate_profile(True, call.from_user.id)
        await call.message.edit_text("Анкета отключена")
        return
    await call.message.delete()


@dp.callback_query_handler(text="activate")
async def activate_profile(call: CallbackQuery):
    await db.deactivate_profile(False, call.from_user.id)
    await call.message.answer("Профиль активирован")
    await call.answer()


@dp.callback_query_handler(kb.user_data.filter())
async def show_user_profile(call: CallbackQuery, callback_data: dict):
    await check_ban(call.from_user.id, call.message)
    user_id = int(callback_data["user_id"])
    data = await db.get_user(user_id)
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await call.message.answer_photo(data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}""", reply_markup=kb.send_sms(user_id))
    await call.answer()


@dp.message_handler(text="Оценивать ➡️")
async def show_estimate(message: Message):
    await check_ban(message.from_user.id, message)
    data = await db.get_user_for_estimate(message.from_user.id)
    if data is None:
        await message.answer("Упс, кажется анкеты закончились")
        return
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await message.answer_photo(data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}""", reply_markup=kb.get_estimate(data["user_id"],
                                                         await db.check_premium(message.from_user.id), 0, 0, 1))


@dp.callback_query_handler(kb.back_data.filter())
async def back_estimate(call: CallbackQuery, callback_data: dict):
    if await db.check_premium(call.from_user.id):
        owner_id = int(callback_data["user_id"])
        data = await db.get_user(owner_id)
        age = data["age"]
        if data["age"] == 0:
            age = "не указано"
        await call.message.answer_photo(data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}""", reply_markup=kb.get_estimate(owner_id,
                                                         await db.check_premium(call.from_user.id), premium=1, back=1))
        await call.message.delete()
    else:
        await call.message.answer(back_premium_error_text, reply_markup=kb.premium)
    await call.answer()


@dp.callback_query_handler(kb.estimate_data.filter())
async def add_new_estimate(call: CallbackQuery, callback_data: dict):
    premium = int(callback_data["premium"])
    owner_id = int(callback_data["user_id"])
    score = callback_data["score"]
    await db.add_new_estimate(call.from_user.id, owner_id, score)

    data = await db.get_user_for_estimate(call.from_user.id, premium)
    if data is None:
        await call.message.answer("Упс, кажется анкеты закончились")
        await call.message.delete()
        return
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await call.message.answer_photo(data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}""", reply_markup=kb.get_estimate(data["user_id"], await db.check_premium(call.from_user.id),
                                                         owner_id, 1 - premium))
    await call.message.delete()


@dp.callback_query_handler(kb.report_data.filter())
async def choose_report(call: CallbackQuery, callback_data: dict):
    user_id = callback_data["user_id"]
    await db.add_new_estimate(call.from_user.id, int(user_id), "skip")
    data = await db.get_user(int(user_id))
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await bot.send_photo(admin_chat, data["photo_id"], caption=f"""✨ Имя: {data["name"]}
    👫 Пол: {data["gender"]}
    🔞 Возраст: {age}
    🏙 Город: {data["city"]}
""", reply_markup=kb.admin_report(user_id, call.from_user.id))
    data = await db.get_user_for_estimate(call.from_user.id)
    if data is None:
        await call.message.answer("Упс, кажется анкеты закончились")
        await call.message.delete()
        return
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await call.message.answer_photo(data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}""", reply_markup=kb.get_estimate(data["user_id"],
                                                         await db.check_premium(call.from_user.id), 0, 0, 1))
    await call.message.delete()


@dp.callback_query_handler(text="cancel", state="*")
async def cancel_other_rep(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.answer()


@dp.callback_query_handler(kb.send_sms_data.filter())
async def start_send_sms(call: CallbackQuery, callback_data: dict, state: FSMContext):
    if await db.check_premium(call.from_user.id):
        user_id = callback_data["user_id"]
        await call.message.answer(send_sms_text, reply_markup=kb.cancel)
        await SmsStates.enter_msg.set()
        await state.update_data(user_id=user_id)
    else:
        await call.message.answer(premium_info_text, reply_markup=kb.premium, parse_mode="HTML")
    await call.answer()


@dp.message_handler(state=SmsStates.enter_msg)
async def send_sms(message: Message, state: FSMContext):
    data = await db.get_user(message.from_user.id)
    receiver_data = await state.get_data()
    await message.bot.send_message(receiver_data["user_id"],
                                   f"Сообщение от {data['name']}, {data['age']}: {message.text}",
                                   reply_markup=kb.send_sms(message.from_user.id))
    await message.answer(finish_sms_text, reply_markup=kb.menu_kb)
    await state.finish()


@dp.message_handler(text="Premium🎗")
async def show_premium_info(message: Message):
    flag, data = await db.check_premium(message.from_user.id, get_date=True)
    if flag:
        date = datetime.utcfromtimestamp(data).strftime('%Y-%m-%d')
        await message.answer(have_premium_free_info_text.format(date=date), reply_markup=kb.premium, parse_mode="HTML")
    else:
        await message.answer(premium_info_text, reply_markup=kb.premium, parse_mode="HTML")


@dp.callback_query_handler(kb.buy_premium_data.filter())
async def set_invoice(call: CallbackQuery, callback_data: dict):
    amount = callback_data["amount"]
    days = callback_data["days"]
    quickpay = Quickpay(
        receiver=yoomoney_id,
        quickpay_form="shop",
        targets="Sponsor this project",
        paymentType="SB",
        sum=amount,
        label=f"{call.from_user.id}_{days}"
    )
    await call.message.edit_text(pay_info_text, reply_markup=kb.get_pay(quickpay.redirected_url))


@dp.callback_query_handler(text="premium_free")
async def show_premium_free_info(call: CallbackQuery):
    text_url = parse.quote(
        f"""Здесь оценят твою привлекательность по фото от 1 до 5 баллов: https://t.me/efanov_dev_bot?start={call.from_user.id}""")
    url = f'https://t.me/share/url?url={text_url}'
    count = await db.get_referals_count(call.from_user.id)
    await call.message.edit_text(premium_free_info_text.format(count=count, user_id=call.from_user.id),
                                 parse_mode="HTML",
                                 reply_markup=kb.get_share(url))


@dp.callback_query_handler(text="back_to_premium_info")
async def back_to_premium_info(call: CallbackQuery):
    flag, data = await db.check_premium(call.from_user.id, get_date=True)
    if flag:
        date = datetime.utcfromtimestamp(data).strftime('%Y-%m-%d')
        await call.message.edit_text(have_premium_free_info_text.format(date=date), reply_markup=kb.premium,
                                     parse_mode="HTML")
    else:
        await call.message.edit_text(premium_info_text, reply_markup=kb.premium, parse_mode="HTML")


@dp.callback_query_handler(text="ask_amnesty")
async def ask_amnesty(call: CallbackQuery):
    await call.message.edit_text(ask_amnesty_text, reply_markup=kb.in_cancel)
    await AmnestyStates.enter_msg.set()


@dp.message_handler(state=AmnestyStates.enter_msg)
async def send_ask_amnesty(message: Message, state: FSMContext):
    data = await db.get_user(int(message.from_user.id))
    age = data["age"]
    if data["age"] == 0:
        age = "не указано"
    await bot.send_photo(admin_chat, data["photo_id"], caption=f"""✨ Имя: {data["name"]}
👫 Пол: {data["gender"]}
🔞 Возраст: {age}
🏙 Город: {data["city"]}

Амнистия: {message.text}""", reply_markup=kb.admin_amnesty(message.from_user.id))
    await message.answer(send_ask_amnesty_text)
    await message.delete()
    await state.finish()


def register_handlers_users(dp: Dispatcher):
    dp.middleware.setup(CheckRegMiddleware())
