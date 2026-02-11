from aiogram import Router, F, html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from sqlalchemy import select, func, update
from dotenv import load_dotenv
import logging
import os

from app.states.AdminStates import Admin
import app.keyboards.admin_kb as kb
from app.keyboards.user_kb import user_main
from app.database.core import async_session
from app.database.models import Topic, Question

admin = Router()

load_dotenv()
@admin.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    admin_id = os.getenv("ADMIN_ID")
    if message.from_user.id == admin_id:
        await message.answer("ПРИВЕТСВУЮ КАПИТАН!",
                             reply_markup=ReplyKeyboardRemove())
        await message.answer("Главное меню админа!",
                             reply_markup=await kb.admin_menu())
    else:
        await message.answer("Неизвестная команда",
                             reply_markup=await user_main())

@admin.callback_query(F.data == "back_to_admin_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
        await callback.message.answer("Главное меню админа!",
                             reply_markup=await kb.admin_menu())
        await callback.answer()

@admin.callback_query(F.data == 'add_quest')
async def start_add_quest(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.question)
    await callback.message.edit_text("Введите название вопроса")
    
@admin.message(StateFilter(Admin.question))
async def options(message: Message, state: FSMContext):
    text_question = message.text
    
    await state.update_data(text_question=text_question)
    await state.set_state(Admin.options)
    
    await message.answer("Теперь введите 5 вариантов ответа через ';;;', <b>НАЧИНАЯ С ПРАВИЛЬНОГО ОТВЕТА!!!</b>")
    
@admin.message(StateFilter(Admin.options))
async def quest_to_topic(message: Message, state: FSMContext):
    options = message.text
    option_list = options.split(";;;")
    correct_option = options.split(";;;")[0]
    topics_text = ""
    correct_index = 0
    
    try:
        if len(option_list) != 5:
            await message.answer("ВНИМАНИЕ ОТВЕТОВ МЕНЬШЕ ПЯТИ!\n\nСОЗДАНИЕ ВОПРОСА ПРЕРАВАНО НАЧНИТЕ ЗАНОВО!",
                                reply_markup=await kb.admin_menu())
        else:
            await state.update_data(options=options,
                                    correct_index=correct_index,
                                    correct_option=correct_option)
            
            async with async_session() as session:
                topic = await session.scalars(select(Topic).order_by(Topic.id))
                topic_list = topic.all()
                
            for topic in topic_list:
                topics_text += f"{topic.id}. <i>{topic.name_topic}</i>\n"
                
            await state.set_state(Admin.quest_to_topic)
            
            await message.answer(f"Напишите id темы:\n{topics_text}")
    except Exception as e:
        logging.error(f"Ошибка при показе тем: {e}")
        await message.answer("Ошибочка вышла!")
        
@admin.message(StateFilter(Admin.quest_to_topic))
async def finall_add_quest(message: Message, state: FSMContext):
    await state.set_state(Admin.check_all_quest)
    data = await state.get_data()   
    topic_id = int(message.text)
    options = data["options"]
    check_option = options.split(';;;')
    correct_index = data['correct_index']
    correct_option = data['correct_option']
    text_question = data['text_question']
    
    await state.update_data(topic_id=topic_id)
    
    await message.answer(f"""
Текст ворпроса: {text_question}\n
Варинаты ответа: {check_option}                  
Правильный ответ: {correct_option} и его индекс {correct_index}
Привязка к теме id: {topic_id}\n
Все ли верно?
""",
                         reply_markup=await kb.yes_or_no())
    
@admin.callback_query(F.data == "yes", StateFilter(Admin.check_all_quest))
async def add_quest_to_bd(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()   
    topic_id = data['topic_id']
    options = data["options"]
    correct_index = data['correct_index']
    text_question = data['text_question']
    try:
        async with async_session() as session:
            topic = await session.scalar(select(Topic).where(Topic.id == topic_id))
            if topic:
                new_quest = Question(
                    text_question=text_question,
                    options=options,
                    correct_index=correct_index,
                    file_id=None,
                    topic_id=topic_id
                )
                
                session.add(new_quest)
                await session.commit()
            
                quest_id = new_quest.id
                await callback.message.edit_text(f"Вопрос №{quest_id} был успешно добавлен",
                                                 reply_markup=await kb.one_more_quest())
            else:
                logging.warning("Тема, которую пытались привязать к вопросу, нет в БД")
                await callback.message.edit_text("Данной темы нет в бд",
                                                 reply_markup=await kb.admin_menu())
    except Exception as e:
        logging.error(f"Ошибка при добавлении вопроса в бд: {e}")
        await callback.message.edit_text("Ошибка добавления вопроса в бд")
    finally:
        await callback.answer()
        await state.clear()
        
@admin.callback_query(F.data == "no", StateFilter(Admin.check_all_quest))
async def cancel_quest_to_bd(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отмена добавления вопроса")
    await callback.message.answer("Главное меню админа!",
                                  reply_markup=await kb.admin_menu())
    await state.clear()
    await callback.answer()

#Add topic
@admin.callback_query(F.data == 'add_topic')
async def get_name_topic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.name_topic)
    await callback.message.edit_text("Введите название темы")
    
@admin.message(StateFilter(Admin.name_topic))
async def get_description(message: Message, state: FSMContext):
    name_topic = message.text
    
    await state.update_data(name_topic=name_topic)
    await state.set_state(Admin.description)
    
    await message.answer('Введите описание темы')
    
@admin.message(StateFilter(Admin.description))
async def check_topic(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await state.set_state(Admin.check)
    
    data = await state.get_data()
    name_topic=data['name_topic']
    
    await message.answer(f"""
Проверьте данные:
Название темы: {name_topic}\n
Описание: {description}
                         """, reply_markup=await kb.yes_or_no())
    
@admin.callback_query(F.data == 'yes',StateFilter(Admin.check))
async def check_topic(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name_topic=data['name_topic']
    description=data['description']
    try:
        async with async_session() as session:
            topic = Topic(
                name_topic=name_topic,
                description=description
            )
            
            session.add(topic)
            await session.commit()
            
        topic_id = topic.id
        await callback.message.edit_text(f"Тема №{topic_id}, добавлена!")
        await callback.message.answer("Главное меню админа!",
                                      reply_markup=await kb.admin_menu())
    except Exception as e:
        logging.error(f"Ошибка добавления темы в бд: {e}")
    finally:
        await callback.answer()
        await state.clear()
        
@admin.callback_query(F.data == 'no',StateFilter(Admin.check))
async def no_check_topic(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отмена добавления темы в бд!")
    await callback.message.answer("Главное меню админа!",
                                  reply_markup=await kb.admin_menu())
    await callback.answer()
    await state.clear()