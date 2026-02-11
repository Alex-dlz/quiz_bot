from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вопрос", callback_data="add_quest")],
        [InlineKeyboardButton(text="Добавить тему", callback_data="add_topic")],
        [InlineKeyboardButton(text="Посмотреть статистику", callback_data="check_info")]
    ])
    
async def yes_or_no():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅Да", callback_data="yes")],
        [InlineKeyboardButton(text="❌Нет", callback_data="no")],
    ])
    
async def one_more_quest():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ДОБАВИТЬ ЕЩЕ ВОПРОС", callback_data="add_quest")],
        [InlineKeyboardButton(text="ГЛАВНОЕ МЕНЮ", callback_data="back_to_admin_menu")],
    ])