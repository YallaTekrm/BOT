import sqlite3
import json
DATABASE_NAME = 'DataBases_YallaTekrm.db'

def init_db():
    """
    يقوم بتهيئة قاعدة البيانات وإنشاء جداول المستخدمين والطلبات المعلقة والإيداعات وسعر الصرف.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # تحديث جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            balance REAL DEFAULT 0.0,
            state TEXT DEFAULT 'none', -- لتتبع حالة المستخدم (مثلاً: 'waiting_for_game_id', 'waiting_for_deposit_amount')
            debt REAL DEFAULT 0.0,
            temp_order_data TEXT -- لتخزين بيانات الطلب مؤقتاً قبل إدخال الـ ID (JSON string)
        )
    """)

    # جدول الإيداعات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            amount REAL NOT NULL,
            wallet_number TEXT NOT NULL,
            transaction_id TEXT NOT NULL,
            deposit_method TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            admin_message_id INTEGER,
            deposit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # جدول سعر الصرف
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id TEXT,
            syr_exchange_usd REAL DEFAULT 0.0,
            registraion_date TEXT DEFAULT CURRENT_TIMESTAMP         
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            quantity TEXT NOT NULL,
            price REAL NOT NULL,
            user_game_id TEXT,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            admin_message_id INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message_report TEXT NOT NULL,
            first_name TEXT NOT NULL,
            report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP               
    )
""")
    conn.commit()
    conn.close()
def add_report_message(user_id, user_message_report, first_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO report (user_id, user_message_report, first_name) VALUES (?,?,?)",(user_id,user_message_report,first_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error sending report message: {e}")
        return None
    finally:
        conn.close()
def add_or_get_user(user_id, username, first_name):
    """
    يضيف مستخدم جديد إلى قاعدة البيانات إذا لم يكن موجوداً بالفعل، ويعيد بياناته.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, state, temp_order_data) VALUES (?, ?, ?, ?, ?)",
                       (user_id, username, first_name, 'none', None))
        conn.commit()
        cursor.execute("SELECT user_id, username, first_name, balance FROM users WHERE user_id = ?",
                       (user_id,))
        user_data = cursor.fetchone()
        return user_data
    except sqlite3.Error as e:
        print(f"Error adding/getting user {e}")
        return None
    finally:
        conn.close()

def get_user_balance(user_id):
    """
    يجلب رصيد المستخدم من قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0.0
    except sqlite3.Error as e:
        print(f"Error getting user balance: {e}")
        return 0.0
    finally:
        conn.close()

def update_user_balance(user_id, amount_to_add):
    """
    يزيد رصيد المستخدم بمبلغ معين. يمكن أن يكون amount_to_add سالب للخصم.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",
                       (amount_to_add, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating user balance: {e}")
        return False
    finally:
        conn.close()

def deduct_balance(user_id, amount):
    """
    يخصم مبلغ معين من رصيد المستخدم.
    """
    if amount <= 0:
        return False
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?", (amount, user_id, amount))
        conn.commit()
        rows_affected = cursor.rowcount
        return rows_affected > 0
    except sqlite3.Error as e:
        print(f"Error deducting balance: {e}")
        return False
    finally:
        conn.close()

def get_user_state(user_id):
    """
    يجلب حالة المستخدم من قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT state FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'none'
    except sqlite3.Error as e:
        print(f"Error getting user state: {e}")
        return 'none'
    finally:
        conn.close()

def set_user_state(user_id, state, temp_data=None):
    """
    يغير حالة المستخدم ويخزن بيانات مؤقتة إذا لزم الأمر.
    temp_data يجب أن تكون سلسلة JSON إذا كانت قاموساً.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET state = ?, temp_order_data = ? WHERE user_id = ?', (state, temp_data, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error setting user state: {e}")
    finally:
        conn.close()
def get_user_temp_order_data(user_id):
    """
    يجلب البيانات المؤقتة لطلب المستخدم من قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT temp_order_data FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return json.loads(result[0])
        return None
    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"Error getting user temp order data: {e}")
        return None
    finally:
        conn.close()

def add_pending_order(user_id, game_name, quantity, price, user_game_id):
    """
    يضيف طلباً جديداً معلقاً إلى قاعدة البيانات ويعيد order_id.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO orders (user_id, game_name, quantity, price, user_game_id)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, game_name, quantity, price, user_game_id))
        order_id = cursor.lastrowid
        conn.commit()
        return order_id
    except sqlite3.Error as e:
        print(f"Error adding pending order: {e}")
        return None
    finally:
        conn.close()

def update_pending_order_status(order_id, status, admin_message_id=None):
    """
    يحدث حالة الطلب المعلق (approved/rejected) ويحفظ ID رسالة الأدمن.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        if admin_message_id:
            cursor.execute('UPDATE orders SET status = ?, admin_message_id = ? WHERE order_id = ?',
                           (status, admin_message_id, order_id))
        else:
            cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?',
                           (status, order_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating pending order status: {e}")
        return False
    finally:
        conn.close()

def get_pending_order_details(order_id):
    """
    يجلب تفاصيل طلب معلق معين.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_id, game_name, quantity, price, user_game_id, status, admin_message_id, order_time FROM orders WHERE order_id = ?', (order_id,))
        result = cursor.fetchone()
        if result:
            return {
                'order_id': order_id, # أضفنا order_id هنا ليكون متاحاً
                'user_id': result[0],
                'game_name': result[1],
                'quantity': result[2],
                'price': result[3],
                'user_game_id': result[4],
                'status': result[5],
                'admin_message_id': result[6],
                'order_time': result[7]
            }
        return None
    except sqlite3.Error as e:
        print(f"Error fetching pending order details: {e}")
        return None
    finally:
        conn.close()
def add_report_message(user_id, username, first_name, message_report):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO report (user_id, username, first_name, message_report) VALUES (?,?,?,?)",(user_id,username,first_name,message_report))
        conn.commit()
        print(f"REPORT message from [{user_id}] was added")
        return None
    except sqlite3.Error as e:
        print(f"Error adding report message from [{user_id}]: {e}")
        return
def save_deposit_to_db(user_id, username, amount, wallet_number, transaction_id, deposit_method):
    """
    يحفظ تفاصيل طلب الإيداع في قاعدة البيانات ويعيد deposit_id.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO deposits (user_id, username, amount, wallet_number, transaction_id, deposit_method)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, amount, wallet_number, transaction_id, deposit_method))
        deposit_id = cursor.lastrowid
        conn.commit()
        print(f"Deposit from user {user_id} saved to DB with ID: {deposit_id}.")
        return deposit_id
    except sqlite3.Error as e:
        print(f"Error saving deposit to DB: {e}")
        return None
    finally:
        conn.close()
def get_debt_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT debt FROM users WHERE user_id = ?",(user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0.0
    except sqlite3.Error as e:
        print(f"Error getting debt amount from user: {user_id}: {e}")
        return 0.0
    finally:
        conn.close()
def deduct_debt(user_id, amount):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor= conn.cursor()
    try:
        cursor.execute("UPDATE users SET debt = debt - ? WHERE user_id = ?",(amount,user_id))
        conn.commit()
        cursor.rowcount > 0
        print(f"The debt has been paid to user id {user_id} in the amount of {amount}")
        return True
    except sqlite3.Error as e:
        print(f"Error Updating [deduct] debt amount: {e}")
        return False
    finally:
        conn.close()
def update_debt_user_amount(user_id, amount):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET debt = debt + ? WHERE user_id = ?",(amount,user_id))
        conn.commit()
        cursor.rowcount > 0
        print(f"Debt ID {user_id} Changed amount to {amount}")
        return True
    except sqlite3.Error as e:
        print(f"Error Updating debt amount: {e}")
        return False
    finally:
        conn.close()
def update_deposit_status_in_db(deposit_id, new_status, admin_message_id=None):
    """
    يحدث حالة الإيداع في قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        if admin_message_id:
            cursor.execute("UPDATE deposits SET status = ?, admin_message_id = ? WHERE id = ?",
                           (new_status, admin_message_id, deposit_id))
        else:
            cursor.execute('UPDATE deposits SET status = ? WHERE id = ?',
                           (new_status, deposit_id))
        conn.commit()
        print(f"Deposit ID {deposit_id} status updated to {new_status}.")
        return True
    except sqlite3.Error as e:
        print(f"Error updating deposit status: {e}")
        return False
    finally:
        conn.close()

def get_deposit_details(deposit_id):
    """
    يجلب تفاصيل الإيداع من قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, username, amount, wallet_number, transaction_id, deposit_method, status, admin_message_id FROM deposits WHERE id = ?", (deposit_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching deposit details: {e}")
        return None
    finally:
        conn.close()

def update_exchange(exchange, admin_id):
    """
    يضيف سعر صرف جديد إلى قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO exchange (syr_exchange_usd, admin_id) VALUES (?, ?)", (exchange, admin_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating exchange rate: {e}")
    finally:
        conn.close()


def get_all_user_ids():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        return user_ids
    except sqlite3.Error as e:
        print(f"Database error in get_all_user_ids: {e}")
        return []
    finally:
        conn.close()

def get_latest_exchange_rate():
    """
    يجلب أحدث سعر صرف من قاعدة البيانات.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT syr_exchange_usd FROM exchange ORDER BY ID DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Error getting latest exchange rate: {e}")
        return None
    finally:
        conn.close()
    
if __name__ == '__main__':
    init_db()
    print("Database initialized and tables ensured.")