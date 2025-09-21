import sqlite3
from info_yt_auto import LEVELS, REWARDS, get_user_level

DB = "DataBases_YallaTekrm.db"

def calc_rewards(level):
    """ احسب كل المكافآت لحد المستوى الحالي """
    return sum(REWARDS[lvl] for lvl in range(1, level+1) if lvl in REWARDS)

def migrate():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            prime_level INTEGER DEFAULT 0,
            balance REAL DEFAULT 0
        )
    """)
    cur.execute("SELECT user_id, SUM(price) FROM orders GROUP BY user_id")
    rows = cur.fetchall()
    for user_id, total in rows:
        total = total or 0
        level, _ = get_user_level(total)
        balance = calc_rewards(level)
        cur.execute("""
            INSERT INTO users (user_id, prime_level, balance)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                prime_level=excluded.prime_level,
                balance=excluded.balance
        """, (user_id, level, balance))
    conn.commit()
    conn.close()
    print("✅ تم تحديث كل المستخدمين حسب مشترياتهم.")

if __name__ == "__main__":
    migrate()
