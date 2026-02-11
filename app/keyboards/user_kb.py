from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def user_main():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Правила игры"), KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Начать игру")]
    ],
                               resize_keyboard=True,
                               input_field_placeholder="Используйте кнопки меню снизу...")
    
async def back_to_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=f"Вернуться в главное меню")]
    ],
                               resize_keyboard=True,
                               input_field_placeholder="Используйте кнопки меню снизу...")
    
async def back_to_menu_inlain():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="back_to_menu")]
    ])
    
async def create_topic(topics_list):
    keyboard = InlineKeyboardBuilder()
    all_topics = topics_list
    for topic in all_topics:
        keyboard.add(InlineKeyboardButton(text=topic.name_topic, callback_data=f"topic_{topic.id}"))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_to_menu"))
    return keyboard.adjust(2).as_markup()

async def select_diff():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Легкий", callback_data="diff_easy")],
        [InlineKeyboardButton(text="Нормальный", callback_data="diff_normall")],
        [InlineKeyboardButton(text="Сложный", callback_data="diff_hard")]
    ])
    
async def create_question_keyboard(finally_options: list, question_id: int):
    keyboard = InlineKeyboardBuilder()
    for idx, option_text in enumerate(finally_options):
        keyboard.add(InlineKeyboardButton(
            text=option_text,  
            callback_data=f"answer_{question_id}_{idx}"  
        ))
    return keyboard.adjust(1).as_markup()