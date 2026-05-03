from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import database as db
import keyboards as kb
from config import ADMIN_ID
import sqlite3
import urllib.request
import json

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет прав.")
        return
    await message.answer("Панель администратора:", reply_markup=kb.admin_main_keyboard())

@router.callback_query(F.data == "admin_orders")
async def list_orders_for_admin(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет прав")
        return
    orders = db.get_all_orders_with_details()
    if not orders:
        await callback.message.answer("Нет заказов.")
        await callback.answer()
        return
    for order in orders[:5]:
        order_id, user_name, user_id, items, total, status, created_at = order
        text = (
            f"🧾 *Заказ #{order_id}*\n"
            f"👤 {user_name} (ID: {user_id})\n"
            f"📅 {created_at[:16]}\n"
            f"📦 {items[:50]}...\n"
            f"💰 {total} руб.\n"
            f"🏷 Статус: *{status}*\n"
        )
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"change_status_{order_id}")]
        ]))
    await callback.answer()

@router.callback_query(F.data.startswith("change_status_"))
async def ask_new_status(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет прав")
        return
    order_id = int(callback.data.split("_")[2])
    order = db.get_order_by_id(order_id)
    if not order:
        await callback.message.answer("Заказ не найден")
        return
    current_status = order[3]
    await callback.message.answer(
        f"Выберите новый статус для заказа #{order_id}\nТекущий: {current_status}",
        reply_markup=kb.status_keyboard(order_id, current_status)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_status_"))
async def update_status(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет прав")
        return
    parts = callback.data.split("_")
    order_id = int(parts[2])
    new_status = "_".join(parts[3:]).replace("_", " ")
    success = db.update_order_status(order_id, new_status)
    if not success:
        await callback.message.answer("Неверный статус")
        return
    order = db.get_order_by_id(order_id)
    if order:
        user_id = order[0]
        try:
            await callback.bot.send_message(user_id, f"🔄 Статус вашего заказа №{order_id} изменён на:\n`{new_status}`\n\nИспользуйте /my_orders для просмотра.", parse_mode="Markdown")
        except:
            pass
    await callback.message.answer(f"✅ Статус заказа #{order_id} обновлён на: {new_status}")
    await callback.answer()

@router.message(Command("all_orders"))
async def all_orders_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет прав.")
        return
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute("SELECT id, user_name, items, status FROM orders ORDER BY id DESC LIMIT 30")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await message.answer("Нет заказов.")
        return
    text = "📋 *Последние заказы:*\n\n"
    for order_id, user_name, items, status in rows:
        short_items = items[:30] + "…" if len(items) > 30 else items
        text += f"`{order_id}` | {user_name} | {short_items} | *{status}*\n"
    await message.answer(text, parse_mode="Markdown")

# КОМАНДА /sync (синхронизация статусов из Google Sheets)
@router.message(Command("sync"))
async def sync_from_google(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет прав.")
        return
    
    url = "https://script.google.com/macros/s/AKfycbx1Qbm6KmIoWL9wxTO8AErmQCafsJ1IoRne_GxVmgK9dl21bjyXrrQjQT4UN4nYPvJU0Q/exec"
    
    await message.answer("🔄 Синхронизация началась...")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        conn = sqlite3.connect('dolls.db')
        cur = conn.cursor()
        updated = 0
        
        for order in data:
            order_id = order.get('id')
            status = order.get('status')
            if order_id and status:
                cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
                updated += cur.rowcount
        
        conn.commit()
        conn.close()
        await message.answer(f"✅ Обновлено статусов: {updated}")
    
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
