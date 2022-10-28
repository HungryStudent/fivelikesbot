from aiogram.utils import executor
from create_bot import dp
from handlers import users
from utils import db


async def on_startup(_):
    pass


users.register_handlers_users(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
