from flask import Flask
import subprocess
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Запускаем Telegram-бота в фоновом режиме
    subprocess.Popen(["python3", "bot.py"])
    time.sleep(2)
    print("Telegram bot started")
    
    # Запускаем веб-сервер
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
