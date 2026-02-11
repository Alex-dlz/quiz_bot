from aiogram.fsm.state import State, StatesGroup

class User(StatesGroup):
    main_menu = State()
    profile = State()
    rule = State()
    
class Game(StatesGroup):
    select_topic = State()
    select_difficult = State()
    first_quest = State()
    second_quest = State()
    third_quest = State()
    fourth_quest = State()
    fifth_quest = State()
    finish_game = State()