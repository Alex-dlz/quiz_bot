from aiogram import Router, Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os
import logging
import asyncio
import sys

from app.utils.constants import TOKEN
from app.handlers.user import user
from app.database.core import init_models
from app.handlers.game import game
from app.handlers.admin import admin

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def main():
    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML
              ))
    
    await init_models()
    
    dp.include_routers(user, game, admin)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)
    
async def startup(dispatcher: Dispatcher):
    print("Bot is starting...")
async def shutdown(dispatcher: Dispatcher):
    print("Bot is stopping...")
    
if __name__ == '__main__':
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")
