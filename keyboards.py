from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.callback_data import CallbackData
from utils import db

user_data = CallbackData("user", "user_id")
change_data = CallbackData("change", "type")
back_data = CallbackData("back", "user_id", "gender")
estimate_data = CallbackData("estimate", "user_id", "score", "premium", "gender")
report_data = CallbackData("report", "user_id", "gender")
send_report_data = CallbackData("send_report", "user_id", "rep_type", "msg")
send_sms_data = CallbackData("send_sms", "user_id")
answer_sms_data = CallbackData("answer_sms", "user_id")
buy_premium_data = CallbackData("buy_premium", "amount", "days")

menu_kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True).add(KeyboardButton('Кто меня оценил❓'),
                                                                     KeyboardButton('Оценивать ➡️')).add(
    KeyboardButton('👤 Мой профиль'),
    KeyboardButton('Premium🎗'),
    KeyboardButton('🏆 TOP'),
    KeyboardButton('Поддержка / О боте 💬'))

my_estimates = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton('Кто меня оценил❓', callback_data=change_data.new("me_estimate")))


async def active_profile(premium_bool):
    kb = InlineKeyboardMarkup(row_width=2)
    if premium_bool:
        kb.add(InlineKeyboardButton('✨ Изменить имя', callback_data=change_data.new("name")),
               InlineKeyboardButton('👫 Изменить пол', callback_data=change_data.new("gender")))
        kb.add(InlineKeyboardButton('🔞 Изменить возраст', callback_data=change_data.new("age")))
        kb.add(InlineKeyboardButton('🏙 Изменить город', callback_data=change_data.new("city")))
        kb.add(InlineKeyboardButton('👤 Добавить Instagram', callback_data=change_data.new("inst")))
        kb.add(InlineKeyboardButton('📸 Изменить фото', callback_data=change_data.new("photo")))
        kb.add(InlineKeyboardButton('🚫 Отключить мою анкету', callback_data="deactivate"))
    else:
        kb.add(InlineKeyboardButton('✨ Изменить имя', callback_data=change_data.new("name")),
               InlineKeyboardButton('👫 Изменить пол', callback_data=change_data.new("gender")))
        kb.add(InlineKeyboardButton('🔞 Изменить возраст', callback_data=change_data.new("age")))
        kb.add(InlineKeyboardButton('🏙 Изменить город', callback_data=change_data.new("city")))
        kb.add(InlineKeyboardButton('🎗 Добавить Instagram', callback_data=change_data.new("inst")))
        kb.add(InlineKeyboardButton('📸 Изменить фото', callback_data=change_data.new("photo")))
        kb.add(InlineKeyboardButton('✅ Включить мою анкету', callback_data="activate"))
    return kb


async def deactive_profile(premium_bool):
    kb = InlineKeyboardMarkup(row_width=2)
    if premium_bool:
        kb.add(InlineKeyboardButton('✨ Изменить имя', callback_data=change_data.new("name")),
               InlineKeyboardButton('👫 Изменить пол', callback_data=change_data.new("gender")))
        kb.add(InlineKeyboardButton('🔞 Изменить возраст', callback_data=change_data.new("age")))
        kb.add(InlineKeyboardButton('🏙 Изменить город', callback_data=change_data.new("city")))
        kb.add(InlineKeyboardButton('👤 Добавить Instagram', callback_data=change_data.new("inst")))
        kb.add(InlineKeyboardButton('📸 Изменить фото', callback_data=change_data.new("photo")))
        kb.add(InlineKeyboardButton('✅ Включить мою анкету', callback_data="activate"))
    else:
        kb.add(InlineKeyboardButton('✨ Изменить имя', callback_data=change_data.new("name")),
               InlineKeyboardButton('👫 Изменить пол', callback_data=change_data.new("gender")))
        kb.add(InlineKeyboardButton('🔞 Изменить возраст', callback_data=change_data.new("age")))
        kb.add(InlineKeyboardButton('🏙 Изменить город', callback_data=change_data.new("city")))
        kb.add(InlineKeyboardButton('🎗 Добавить Instagram', callback_data=change_data.new("inst")))
        kb.add(InlineKeyboardButton('📸 Изменить фото', callback_data=change_data.new("photo")))
        kb.add(InlineKeyboardButton('✅ Включить мою анкету', callback_data="activate"))
    return kb

deactive_profile = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton('✨ Изменить имя', callback_data=change_data.new("name")),
    InlineKeyboardButton('👫 Изменить пол', callback_data=change_data.new("gender")),
    InlineKeyboardButton('🔞 Изменить возраст', callback_data=change_data.new("age")),
    InlineKeyboardButton('🏙 Изменить город', callback_data=change_data.new("city")),
    InlineKeyboardButton('🎗 Добавить Instagram', callback_data=change_data.new("inst")),
    InlineKeyboardButton('📸 Изменить фото', callback_data=change_data.new("photo"))).add(
    InlineKeyboardButton('✅ Включить мою анкету', callback_data="activate"))

accept_deactivate = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Отключить", callback_data="deactivate_accept"),
    InlineKeyboardButton("Не отключать", callback_data="deactivate_cancel"))

estimate_gender = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("👱🏻‍♂️М", callback_data="estimate_gender_m"),
    InlineKeyboardButton("👩🏻‍🦳 Ж", callback_data="estimate_gender_f"),
    InlineKeyboardButton("👫 Всех", callback_data="estimate_gender_all"))

gender = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("👱🏻‍♂️М", callback_data="gender_m"),
                                               InlineKeyboardButton("👩🏻‍🦳 Ж", callback_data="gender_f"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отмена"))
in_cancel = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Отмена", callback_data="cancel"))
admin_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отменить"))

premium = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Неделя Premium, 99 rub", callback_data=buy_premium_data.new(99, 1)),
    InlineKeyboardButton("Месяц Premium, 219 rub", callback_data=buy_premium_data.new(219, 3)),
    InlineKeyboardButton("2 месяца Premium, 429 rub", callback_data=buy_premium_data.new(429, 7)),
    InlineKeyboardButton("6 месяцев Premium, 1255 rub", callback_data=buy_premium_data.new(1255, 7)),
    InlineKeyboardButton("Год Premium, 2499 rub", callback_data=buy_premium_data.new(2499, 7)),
    InlineKeyboardButton("Получить бесплатно", callback_data="premium_free"))

ask_amnesty = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Обжаловать решение", callback_data="ask_amnesty"))

change_photo = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("Да", callback_data="change_photo_acc"),
                                                     InlineKeyboardButton("Нет", callback_data="change_photo_can"))


def get_partner(partner_url):
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Подписаться", url=partner_url))


async def get_top(top_time):
    kb = InlineKeyboardMarkup(row_width=1)
    if top_time == "all":
        data = await db.get_top()
    else:
        data = await db.get_today_top()
    pos = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, user in enumerate(data):
        rating = user['rating']
        if rating is None:
            rating = 0
        kb.add(InlineKeyboardButton(f"{pos[i]} {user['name']} - {round(rating, 1)}",
                                    callback_data=user_data.new(user['user_id'])))
    if top_time == "all":
        kb.add(InlineKeyboardButton("За сегодня", callback_data="top_today"))
    else:
        kb.add(InlineKeyboardButton("За всё время", callback_data="top_all"))

    return kb


def get_estimate(user_id, have_premium, selected_gender, owner_id=0, premium_bool=1, back=0):
    kb = InlineKeyboardMarkup(row_width=5)
    score_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(5):
        kb.insert(InlineKeyboardButton(score_emoji[i],
                                       callback_data=estimate_data.new(user_id, i + 1, premium_bool, selected_gender)))
    sms_text = "🎗Написать"
    back_text = "🎗 Назад"
    if have_premium:
        sms_text = "Написать"
        back_text = "⬅ Назад"
    if not back:
        kb.add(InlineKeyboardButton(back_text, callback_data=back_data.new(owner_id, selected_gender)),
               InlineKeyboardButton(sms_text, callback_data=send_sms_data.new(user_id)))
    else:
        kb.add(InlineKeyboardButton(sms_text, callback_data=send_sms_data.new(user_id)))
    kb.add(InlineKeyboardButton("⛔️Пожаловаться", callback_data=report_data.new(user_id, selected_gender)))
    return kb


def me_estimates(count, user_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Отправить сообщение", callback_data=send_sms_data.new(user_id)))
    if count != 0:
        kb.add(InlineKeyboardButton(f"Следующий (ещё {count})", callback_data="next_estimate"))
    return kb


def get_report(user_id, msg):
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("18+", callback_data=send_report_data.new(user_id, "1", msg)),
        InlineKeyboardButton("Оскорбление", callback_data=send_report_data.new(user_id, "2", msg)),
        InlineKeyboardButton("Спам", callback_data=send_report_data.new(user_id, "3", msg)),
        InlineKeyboardButton("Другое", callback_data=send_report_data.new(user_id, "other", msg)),
        InlineKeyboardButton("Назад", callback_data="cancel_report"))


def send_sms(user_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Отправить сообщение", callback_data=send_sms_data.new(user_id)))


def answer_sms(user_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Отправить сообщение", callback_data=answer_sms_data.new(user_id)))


def get_share(url):
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Поделиться", url=url),
                                                 InlineKeyboardButton("Назад", callback_data="back_to_premium_info"))


def admin_report(user_id, reporter_id):
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("Забанить", callback_data=f"ban_{user_id}_{reporter_id}"),
        InlineKeyboardButton("Отклонить жалобу", callback_data="admin_dismiss_report"))


def admin_amnesty(user_id):
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("Разбанить", callback_data=f"unban_{user_id}"),
        InlineKeyboardButton("Отклонить заявку", callback_data="admin_dismiss_amnesty"))


def get_pay(url):
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Банковская карта", web_app=WebAppInfo(url=url)),
                                                 InlineKeyboardButton("YooMoney", web_app=WebAppInfo(url=url)))
