import sqlite3

ORDER_STATUSES = [
    "оформлен",
    "в пути на склад в США",
    "в пути на склад в Европе",
    "в пути на склад в Казахстан",
    "на пути в РФ",
    "таможня в РФ",
    "Отправлен администратору"
]

def init_db():
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            photo_file_id TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            items TEXT,
            total REAL,
            status TEXT DEFAULT 'оформлен',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_orders_with_details():
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute("SELECT id, user_name, user_id, items, total, status, created_at FROM orders ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_order_by_id(order_id):
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id, items, total, status FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_order_status(order_id, new_status):
    if new_status not in ORDER_STATUSES:
        return False
    conn = sqlite3.connect('dolls.db')
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
    conn.commit()
    conn.close()
    return True
