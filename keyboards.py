from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_admin")]
    ])

def admin_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders")]
    ])

def status_keyboard(order_id, current_status):
    from database import ORDER_STATUSES
    buttons = []
    for status in ORDER_STATUSES:
        if status == current_status:
            text = f"✅ {status}"
        else:
            text = f"➡️ {status}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"set_status_{order_id}_{status}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
