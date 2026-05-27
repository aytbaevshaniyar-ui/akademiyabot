import sqlite3
from typing import Optional, List, Dict

class Database:
    def __init__(self, path: str = "bot.db"):
        self.path = path
        self._init()

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self):
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username    TEXT,
                    joined_at   TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    work_type  TEXT NOT NULL,
                    topic      TEXT NOT NULL,
                    pages      TEXT NOT NULL,
                    price      INTEGER NOT NULL,
                    status     TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.commit()

    # ── USERS ──────────────────────────────────────
    def add_user(self, telegram_id: int, username: str):
        with self._conn() as c:
            c.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?,?)",
                (telegram_id, username)
            )
            c.commit()

    # ── ORDERS ─────────────────────────────────────
    def create_order(self, user_id: int, work_type: str,
                     topic: str, pages: str, price: int) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO orders (user_id,work_type,topic,pages,price) VALUES (?,?,?,?,?)",
                (user_id, work_type, topic, pages, price)
            )
            c.commit()
            return cur.lastrowid

    def get_order(self, order_id: int) -> Optional[Dict]:
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM orders WHERE id=?", (order_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_user_orders(self, user_id: int) -> List[Dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, order_id: int, status: str):
        with self._conn() as c:
            c.execute(
                "UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (status, order_id)
            )
            c.commit()

    # ── STATS ──────────────────────────────────────
    def get_stats(self) -> Dict:
        with self._conn() as c:
            users     = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total     = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            completed = c.execute("SELECT COUNT(*) FROM orders WHERE status='completed'").fetchone()[0]
            pending   = c.execute("SELECT COUNT(*) FROM orders WHERE status IN ('pending','waiting','generating')").fetchone()[0]
            rejected  = c.execute("SELECT COUNT(*) FROM orders WHERE status='rejected'").fetchone()[0]
            revenue   = c.execute("SELECT COALESCE(SUM(price),0) FROM orders WHERE status='completed'").fetchone()[0]
            return {
                "users": users, "total": total,
                "completed": completed, "pending": pending,
                "rejected": rejected, "revenue": revenue
            }
