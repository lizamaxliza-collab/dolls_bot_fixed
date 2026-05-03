from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Запускаем бота в фоновом процессе
    subprocess.Popen(["python3", "bot.py"])

    # Правильно получаем порт из переменной окружения PORT
    port = int(os.environ.get("PORT", 8080))
    # Главное правило: привязываемся к адресу 0.0.0.0
    app.run(host='0.0.0.0', port=port)
