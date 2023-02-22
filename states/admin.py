from aiogram.dispatcher.filters.state import StatesGroup, State


class SendStates(StatesGroup):
    enter_text = State()