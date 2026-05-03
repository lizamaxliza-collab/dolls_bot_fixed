from flask import Flask
import threading
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from user_handlers import router as user_router
from admin_handlers import router as admin_router
import asyncio
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(admin_router)
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
