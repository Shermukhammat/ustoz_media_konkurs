from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    get_number = State()
    update_number = State()
    update_name = State()
    