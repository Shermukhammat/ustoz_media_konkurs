from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    get_number = State()
    update_number = State()
    update_name = State()


class RegisterStates(StatesGroup):
    check_sub = State()
    get_number = State()
    

class AdminPanel(StatesGroup):
    main = State()

    get_ads_media = State()
    get_ads_button = State()
    confirm_ads_send = State()

    add_admin = State()
    remove_admin = State()