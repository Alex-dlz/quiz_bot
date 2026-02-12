from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func, update
import random
import logging
from datetime import datetime

from app.states.UserState import Game
from app.database.core import async_session
from app.database.models import Topic, Question, UserProfile
import app.keyboards.user_kb as kb


game = Router()


def queze(x, option_list, correct_index):
    wrong_option = [opt for i, opt in enumerate(option_list) 
                    if i != correct_index]
    random_wrong = random.sample(wrong_option, min(x, len(wrong_option)))
    
    correct_option = option_list[correct_index]
    finally_options = random_wrong + [option_list[correct_index]]
    random.shuffle(finally_options)
    new_correct_index = finally_options.index(correct_option)
    return finally_options, new_correct_index


@game.message(F.text == "Начать игру")
async def select_diff(message: Message, state: FSMContext):
    await state.set_state(Game.select_difficult)
    await message.answer("НАЧИНАЕМ ИГРУ!", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите уровень сложности:\n"
                         "От этого зависит, какое количество вариантов ответа будет предложено и сколько времени у вас есть на выбор ответа.",
                         reply_markup=await kb.select_diff()
                         )


@game.callback_query(F.data.startswith("diff_"))
async def select_topic(callback: CallbackQuery, state: FSMContext):
    
    difficult = callback.data.split("_")[1]
    await state.update_data(difficult=difficult)
    await state.set_state(Game.select_topic)
    
    try:
        async with async_session() as session:
            topics = await session.scalars(select(Topic))
            topics_list = topics.all()

        await callback.message.edit_text("Выберите тему для викторины:",
                             reply_markup=await kb.create_topic(topics_list))        
    except Exception as e:
        logging.error(f"Ошибка при показе тем: {e}")
        await callback.message.answer("Ошибка показа тем", reply_markup=await kb.back_to_menu())
    finally:
        await callback.answer()
        
        
@game.callback_query(F.data.startswith("topic_"))
async def select_diff(callback: CallbackQuery, state: FSMContext):
    
    topic_id = callback.data.split("_")[1]
    data = await state.get_data()
    level = data.get("difficult")
    try:
        async with async_session() as session:
            try:
                questions = await session.scalars(
                    select(Question)
                    .where(Question.topic_id == int(topic_id))
                    .order_by(func.random())
                    .limit(5)
                )

            except Exception as e:
                logging.error(f"Ошибка при получении вопросов: {e}")
                await callback.message.edit_text("Ошибка при получении вопросов")

            question_list = list(questions)
            first_question = question_list[0]
            option_list = first_question.options.split(";;;")
            question_id = first_question.id
            option_index = first_question.id
            first_question_id = question_list[0].id
            second_question_id = question_list[1].id
            third_question_id = question_list[2].id
            fourth_question_id = question_list[3].id
            fifth_question_id = question_list[4].id
            if len(question_list) < 5:
                    logging.error("В этой теме недостаточно вопросов для викторины.")
                    await callback.message.edit_text("В этой теме недостаточно вопросов для викторины, выберите другую тему!",
                                                     reply_markup=await kb.back_to_menu_inlain())   
                    return   

        if level == "easy":
            x = 2
        elif level == "normall":
            x = 3
        else:
            x = 4
            
        finally_options, new_correct_index = queze(x, option_list, first_question.correct_index)    
        
        await state.update_data(
            questions = question_list,
            correct_answer = 0,
            current_question_index = 0,
            option_index = option_index,
            new_correct_index = new_correct_index,
            x = x ,
            first_question_id = first_question_id,
            second_question_id = second_question_id,
            third_question_id = third_question_id,
            fourth_question_id = fourth_question_id,
            fifth_question_id = fifth_question_id
        )
        
        
        await callback.message.edit_text("Вопрос номер 1 из 5. \n"
                                        f"{first_question.text_question}",
                                        reply_markup=await kb.create_question_keyboard(finally_options, question_id))
            
    except Exception as e:
        logging.error(f"Не удалось получить вопросы ошибка: {e}")
        await callback.message.edit_text("Не удалось получить вопросы")
            
                    
@game.callback_query(F.data.startswith("answer_"))
async def check_answer_and_next_question(callback: CallbackQuery, state: FSMContext):
    
    user_answer_id = int(callback.data.split("_")[2])
    tg_id = callback.from_user.id
    data = await state.get_data()
    
    question_list = data["questions"]
    correct_answer = data["correct_answer"]
    current_question_index = data["current_question_index"]
    new_correct_index = data["new_correct_index"]
    first_question_id = data["first_question_id"]
    second_question_id = data["second_question_id"]
    third_question_id = data["third_question_id"]
    fourth_question_id = data["fourth_question_id"]
    fifth_question_id = data["fifth_question_id"]
    x = int(data["x"])

    try:
        if user_answer_id == new_correct_index:
            correct_answer += 1
            await callback.answer("✅Правильно")
        else:
            await callback.answer("❌Неправильно")
        await state.update_data(correct_answer=correct_answer)
    except Exception as e:
        logging.error(f"Ошибка с id: {e}")
        await callback.answer("Ошибка проверки ответа")

    next_question_index = current_question_index + 1
    
    try:

        if next_question_index < len(question_list):
            next_question = question_list[next_question_index]
            option_list = next_question.options.split(";;;")
            finally_options, new_correct_index = queze(x, option_list, next_question.correct_index)
            await callback.answer()            
            await state.update_data(current_question_index=next_question_index,
                                    new_correct_index = new_correct_index)
            await callback.message.edit_text(f"Вопрос номер {next_question_index + 1} из 5. \n{next_question.text_question}",
                                            reply_markup=await kb.create_question_keyboard(finally_options, next_question.id))
        else: 
            experience = correct_answer * x * 5
            

            
            try:
                async with async_session() as session:
                    user = await session.scalar(select(UserProfile).where(UserProfile.tg_id == tg_id))
                    quest1 = await session.scalar(select(Question).where(Question.id == first_question_id))
                    quest2 = await session.scalar(select(Question).where(Question.id == second_question_id))
                    quest3 = await session.scalar(select(Question).where(Question.id == third_question_id))
                    quest4 = await session.scalar(select(Question).where(Question.id == fourth_question_id))
                    quest5 = await session.scalar(select(Question).where(Question.id == fifth_question_id))
                    
                    if user: 
                        user.total_games += 1
                        user.total_correct += correct_answer
                        user.last_active = datetime.now()
                        user.exp += experience
                        logging.info(f"Обновлен пользователь {tg_id}: +{experience} опыта")
                        
                        await session.commit()
                    else:
                        username = callback.from_user.username
                        name = html.quote(callback.from_user.first_name or "")
                        new_user = UserProfile(
                            tg_id=tg_id,
                            first_name=name,
                            username=username,
                            total_games=1,
                            total_correct=correct_answer,
                            exp=experience,
                            level=1,
                            status="Новичок",
                            joined_at=datetime.now()
                        )
                        session.add(new_user)
                        await session.commit()
            
            except Exception as e:
                logging.error(f"Не удалось обновить данные пользователя: {e}")
                await callback.answer("НЕ УДАЛОСЬ ОБНОВИТЬ ДАННЫЕ")
            await callback.message.edit_text(f"""
<b>🎉Поздравляю! Вы прошли викторину!🎉</b>

✅Колличество правильных ответов: {correct_answer} из {len(question_list)}
⭐Получено опыта: <code>{experience}</code>

<b>Отгадки викторины:</b>

1.  {quest1.text_question}
     Правильный ответ: <i> {quest1.options.split(";;;")[0]}</i>

2.  {quest2.text_question}
     Правильный ответ: <i> {quest2.options.split(";;;")[0]}</i>

3.  {quest3.text_question}
     Правильный ответ: <i> {quest3.options.split(";;;")[0]}</i>

4.  {quest4.text_question}
     Правильный ответ: <i> {quest4.options.split(";;;")[0]}</i>

5.  {quest5.text_question}
     Правильный ответ: <i> {quest5.options.split(";;;")[0]}</i>
""", 
                                            reply_markup=await kb.back_to_menu_inlain())
    except Exception as e:
        logging.error(f"Ошибка при новом вопросе: {e}")
        await callback.message.answer("Ошибка при новом вопросе")
