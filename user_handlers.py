import sqlite3
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMIN_ID

router = Router()
user_questions = {}

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Мои заказы", callback_data="my_orders")],
    [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_admin")]
])

@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("👋 Добро пожаловать!", reply_markup=start_kb)

@router.message(Command("my_orders"))
async def my_orders_cmd(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute("SELECT id, items, total, status, created_at FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await message.answer("У вас нет привязанных заказов. Используйте /link НОМЕР_ЗАКАЗА")
        return
    text = "📋 *Ваши заказы:*\n\n"
    for order_id, items, total, status, created_at in rows:
        text += f"*Заказ #{order_id}* от {created_at[:10]}\n{items[:50]}\n💰 {total} руб.\n🏷 Статус: `{status}`\n\n"
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("link"))
async def link_cmd(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Используйте: /link НОМЕР_ЗАКАЗА")
        return
    try:
        order_id = int(args[1])
    except:
        await message.answer("Номер заказа должен быть числом.")
        return
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute("SELECT user_name FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    if not row:
        await message.answer("Заказ не найден.")
        conn.close()
        return
    user_name = row[0]
    cur.execute("UPDATE orders SET user_id=? WHERE user_name=?", (message.from_user.id, user_name))
    conn.commit()
    updated = cur.rowcount
    conn.close()
    await message.answer(f"✅ Привязано {updated} заказов.")

@router.callback_query(F.data == "my_orders")
async def my_orders_callback(callback: CallbackQuery):
    await my_orders_cmd(callback.message)
    await callback.answer()

@router.callback_query(F.data == "ask_admin")
async def ask_admin_callback(callback: CallbackQuery):
    await callback.message.answer("📝 Напишите ваш вопрос. Администратор ответит.")
    await callback.answer()

@router.message(F.text & ~F.command)
async def forward_question(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    await message.forward(ADMIN_ID)
    await message.answer("✅ Вопрос отправлен.")
