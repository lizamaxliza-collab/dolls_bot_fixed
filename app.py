from flask import Flask
import threading
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from user_handlers import router as user_router
from admin_handlers import router as admin_router
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    # Создаём новый цикл событий для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(admin_router)
    
    # Запускаем бота с обработкой ошибок
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except Exception as e:
        print(f"Ошибка бота: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер в главном потоке
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
