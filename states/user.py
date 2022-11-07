from aiogram.dispatcher.filters.state import StatesGroup, State


class RegStates(StatesGroup):
    enter_name = State()
    enter_gender = State()
    enter_photo = State()



class ChangeStates(StatesGroup):
    change_name = State()
    change_age = State()
    change_city = State()
    change_inst = State()
    change_photo = State()


class ReportStates(StatesGroup):
    enter_msg = State()


class SmsStates(StatesGroup):
    enter_msg = State()
    enter_answer = State()


class AmnestyStates(StatesGroup):
    enter_msg = State()
