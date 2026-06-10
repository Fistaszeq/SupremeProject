"""
Moduł bazy danych dla aplikacji budżetowej.
"""

import os
import sqlite3
from datetime import date

DB_DIR = os.path.join("data")
DB_FILE = os.path.join(DB_DIR, "simple_budget.sqlite3")

class SimpleBudgetDB:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    balance REAL NOT NULL DEFAULT 0,
                    color TEXT NOT NULL DEFAULT '#2563EB'
                );
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#10B981'
                );
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    amount REAL NOT NULL,
                    account_id INTEGER NOT NULL,
                    tag TEXT NOT NULL DEFAULT 'Inne',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_DATE,
                    FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
                );
                """
            )
            
            cur.execute("SELECT COUNT(*) FROM tags")
            if cur.fetchone()[0] == 0:
                cur.executemany(
                    "INSERT INTO tags (name, color) VALUES (?, ?)",
                    [
                        ("Jedzenie", "#F97316"),
                        ("Transport", "#3B82F6"),
                        ("Mieszkanie", "#8B5CF6"),
                        ("Rozrywka", "#EC4899"),
                        ("Inne", "#64748B"),
                    ],
                )

    def close(self):
        self.conn.close()

    def accounts(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT a.*, 
                   (SELECT created_at FROM transactions WHERE account_id = a.id ORDER BY id DESC LIMIT 1) as last_date,
                   (SELECT amount FROM transactions WHERE account_id = a.id ORDER BY id DESC LIMIT 1) as last_amount,
                   (SELECT kind FROM transactions WHERE account_id = a.id ORDER BY id DESC LIMIT 1) as last_kind
            FROM accounts a
            ORDER BY a.id
        """)
        return [dict(r) for r in cur.fetchall()]

    def add_account(self, name, balance, color):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO accounts(name, balance, color) VALUES (?, ?, ?)", 
                        (name, float(balance), color))
            return cur.lastrowid

    def update_account(self, account_id, name, balance, color):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("UPDATE accounts SET name = ?, balance = ?, color = ? WHERE id = ?", 
                        (name, float(balance), color, int(account_id)))

    def delete_account(self, account_id):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute("DELETE FROM accounts WHERE id = ?", (int(account_id),))

    def add_transaction(self, kind, amount, account_id, tag, note, tx_date=None):
        if not tx_date:
            tx_date = str(date.today())
            
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO transactions(kind, amount, account_id, tag, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (kind, float(amount), int(account_id), tag, note, tx_date),
            )
            
            if kind == "Wpłata":
                cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (float(amount), int(account_id)))
            else:
                cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (float(amount), int(account_id)))
            
            return cur.lastrowid

    def transactions(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT t.*, a.name AS account_name
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            ORDER BY t.id DESC
            LIMIT 20
            """
        )
        return [dict(r) for r in cur.fetchall()]

    def tags(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tags ORDER BY id")
        return [dict(r) for r in cur.fetchall()]

    def stats(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT tag,
                   SUM(CASE WHEN kind='Wypłata' THEN amount ELSE 0 END) AS spent,
                   SUM(CASE WHEN kind='Wpłata' THEN amount ELSE 0 END) AS income
            FROM transactions
            GROUP BY tag
            ORDER BY spent DESC
            """
        )
        return [dict(r) for r in cur.fetchall()]

    def account_stats(self, account_id):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT tag,
                   SUM(CASE WHEN kind='Wypłata' THEN amount ELSE 0 END) AS spent,
                   SUM(CASE WHEN kind='Wpłata' THEN amount ELSE 0 END) AS income
            FROM transactions
            WHERE account_id = ?
            GROUP BY tag
            ORDER BY spent DESC
            """, (int(account_id),)
        )
        return [dict(r) for r in cur.fetchall()]