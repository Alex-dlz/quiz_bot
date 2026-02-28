from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import logging
import asyncio

import app.keyboards.user_kb as kb
from app.states.UserState import User
from app.database.models import UserProfile
from app.database.core import async_session
from app.utils.constants import RULE, MAIN_MENU, HELP


user = Router()

#@user.message(Command("id"))
#async def check_id(message: Message):
#    id = message.from_user.id
#    await message.answer(f"{id}")

@user.message(CommandStart())
@user.message(F.text == "Вернуться в главное меню")
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(User.main_menu)  
    await message.answer(
        MAIN_MENU, 
        reply_markup=await kb.user_main()
    )

@user.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(HELP)
    
@user.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(User.main_menu) 

    await callback.message.delete()

    await callback.message.answer(
        MAIN_MENU,
        reply_markup=await kb.user_main()
    )
    await callback.answer()
    

@user.message(F.text == "Профиль")
async def check_profile(message: Message, state: FSMContext):
    await state.set_state(User.profile)
    name = html.quote(message.from_user.first_name or "")
    tg_id = message.from_user.id
    username = message.from_user.username
    try:
        async with async_session() as session:
            user = await session.scalar(select(UserProfile).where(UserProfile.tg_id == tg_id))
            if user:
                accuracy = await user.recalc_accuracy
                level, status = await user.recalc_status
                await message.answer(f"""
<b>👤 Профиль {name}</b>
<i>{status}</i>

<u>📊 Статистика:</u>
🎮 Игр сыграно: <code>{user.total_games}</code>
✅ Правильных ответов: <code>{user.total_correct}</code>
🎯 Точность: <code>{accuracy}%</code>

<u>📈 Прогресс:</u>
⭐ Уровень: <code>{level}</code>
🔥 Опыт: <code>{user.exp}</code>""",
                reply_markup=await kb.back_to_menu()
                )
            else:
                new_user = UserProfile(
                    tg_id=tg_id,
                    first_name=name,
                    username=username,
                    total_games=0,
                    total_correct=0,
                    accuracy=0.0,
                    exp=0,
                    level=1,
                    status="Новичок"
                )
                session.add(new_user)
                await session.commit()
                
                accuracy = await new_user.recalc_accuracy
                status = html.quote(new_user.status)
                
                await message.answer(f"""
<b>👤 Профиль {name}</b>
<i>{status}</i>

<u>📊 Статистика:</u>
🎮 Игр сыграно: <code>{new_user.total_games}</code>
✅ Правильных ответов: <code>{new_user.total_correct}</code>
🎯 Точность: <code>{accuracy}%</code>

<u>📈 Прогресс:</u>
⭐ Уровень: <code>{new_user.level}</code>
🔥 Опыт: <code>{new_user.exp}</code>""",
                reply_markup=await kb.back_to_menu()
                )
    except Exception as e:
        logging.error(f"Не получилось показать статистику, ошибка {e}")
        await message.answer("Не получилось показать статистику профиля",
                             reply_markup=await kb.back_to_menu())
    
@user.message(F.text == "Правила игры")
async def check_rules(message: Message, state: FSMContext):
    await state.set_state(User.rule)
    await message.answer(RULE, reply_markup=await kb.back_to_menu())