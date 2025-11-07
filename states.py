from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    get_number = State()
    update_number = State()
    update_name = State()


class RegisterStates(StatesGroup):
    check_sub = State()
    get_number = State()
    