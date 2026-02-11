from aiogram.fsm.state import State, StatesGroup

class Admin(StatesGroup):
    admin_menu = State()
    #Add question
    question = State()
    options = State()
    quest_to_topic = State()
    check_all_quest = State()
    #add_topic
    name_topic = State()
    description = State()
    check = State()