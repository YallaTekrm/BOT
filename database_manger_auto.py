import sqlite3

DB = "AUTO_DB_PRODUCTS.db"

def __init__():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                first_name TEXT,
                service TEXT NOT NULL,
                quantity TEXT NOT NULL,
                price REAL NOT NULL,
                num_id TEXT NOT NULL,
                api_order_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS api(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id REAL NOT NULL,
                api TEXT DEFAULT 'AWAITING_API',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error Creating DB: {e}")
    finally:
        conn.close()


def add_pending_order(user_id, first_name, service, quantity, price, num_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO orders (user_id, first_name, service, quantity, price, num_id)
            VALUES (?,?,?,?,?,?)
            """,
            (user_id, first_name, service, quantity, price, num_id)
        )
        conn.commit()
        return cursor.lastrowid  # id المحلي للسجل
    except sqlite3.Error as e:
        print(f"Error adding pending order to DB: {e}")
        return None
    finally:
        conn.close()

def update_api(id, api):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE api SET api = ? WHERE id = ?",(api,id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating API: [{e}]")
        return False
    finally:
        conn.close()
def update_order_status(order_id, status):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating status where api_order_id: [{order_id}]: {e}")
        return False
    finally:
        conn.close()

def get_api():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT api FROM api ORDER BY ID DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else 'none'
    except sqlite3.Error as e:
        print(f"Error Getting API: [{e}]")
        return 'none'
    finally:
        conn.close()
def get_user_total(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT SUM(price) FROM orders WHERE user_id = ?", (user_id,))
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0
def get_user_info(user_id):
    conn = sqlite3.connect("DataBases_YallaTekrm.db")
    cur = conn.cursor()
    cur.execute("SELECT prime_level, balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO users (user_id, prime_level, balance) VALUES (?, ?, ?)", (user_id, 0, 0))
        conn.commit()
        conn.close()
        return 0, 0
    conn.close()
    return row[0], row[1]

def update_user(user_id, new_level=None, add_balance=0):
    conn = sqlite3.connect("DataBases_YallaTekrm.db")
    cur = conn.cursor()
    if new_level is not None:
        cur.execute("UPDATE users SET prime_level=?, balance=balance+? WHERE user_id=?", (new_level, add_balance, user_id))
    else:
        cur.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (add_balance, user_id))
    conn.commit()
    conn.close()