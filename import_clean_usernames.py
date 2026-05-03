import gspread
from google.oauth2.service_account import Credentials
import sqlite3

GC_ID = "15rkVOSA5D2VLHRM2juajQWnvqOE2DNu_Zeatd6y_paI"

# Настройка столбцов
username_col = 'C'   # юзернейм клиента
items_col = 'B'      # название товара
price_col = 'E'      # цена
status_col = 'H'     # статус
tg_id_col = 'D'      # Telegram ID

print("🚀 Импорт заказов из Google Таблицы...")

scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file('google_key.json', scopes=scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(GC_ID)

def col_index(letter):
    return ord(letter.upper()) - 65

conn = sqlite3.connect('dolls.db')
cur = conn.cursor()

# Очищаем старые заказы (чтобы не было дублей)
cur.execute("DELETE FROM orders")
print("Старая база очищена")

next_id = 1
total_added = 0

for sheet in spreadsheet.worksheets():
    sheet_name = sheet.title
    print(f"\n📄 Лист: {sheet_name}")
    all_values = sheet.get_all_values()
    if len(all_values) < 2:
        continue

    added = 0
    for row in all_values[1:]:
        if len(row) <= col_index(username_col):
            continue
        username = row[col_index(username_col)].strip()
        if not username:
            continue
        
        if username.startswith('@'):
            username = username[1:]
        
        items = row[col_index(items_col)] if len(row) > col_index(items_col) else ''
        price_str = row[col_index(price_col)] if len(row) > col_index(price_col) else '0'
        try:
            total = float(price_str.replace(',', '.').replace(' ', ''))
        except:
            total = 0.0
        status = row[col_index(status_col)] if len(row) > col_index(status_col) else 'оформлен'
        status = status.lstrip('#')
        tg_id = 0
        if len(row) > col_index(tg_id_col) and row[col_index(tg_id_col)].isdigit():
            tg_id = int(row[col_index(tg_id_col)])

        cur.execute('''
            INSERT INTO orders (id, user_id, user_name, items, total, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (next_id, tg_id, username, items, total, status))
        
        added += 1
        next_id += 1

    print(f"   ✅ Добавлено {added} заказов")
    total_added += added

conn.commit()
conn.close()
print(f"\n🎉 Итого добавлено {total_added} заказов")
