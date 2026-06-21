"""
Moduł bazy danych dla aplikacji budżetowej.
"""

import calendar
import os
import sqlite3
from datetime import date, datetime, timedelta

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
                CREATE TABLE IF NOT EXISTS recurring_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    amount REAL NOT NULL,
                    account_id INTEGER NOT NULL,
                    tag TEXT NOT NULL DEFAULT 'Inne',
                    note TEXT NOT NULL DEFAULT '',
                    frequency TEXT NOT NULL DEFAULT 'Miesięcznie',
                    next_date TEXT NOT NULL DEFAULT CURRENT_DATE,
                    active INTEGER NOT NULL DEFAULT 1,
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

    def update_transaction(self, transaction_id, kind, amount, account_id, tag, note, tx_date):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT kind, amount, account_id FROM transactions WHERE id = ?", (int(transaction_id),))
            old = cur.fetchone()
            if old is None:
                raise ValueError("Transakcja nie istnieje")

            old_kind, old_amount, old_account_id = old[0], float(old[1]), int(old[2])
            old_effect = old_amount if old_kind == "Wpłata" else -old_amount
            new_effect = float(amount) if kind == "Wpłata" else -float(amount)

            if old_account_id == int(account_id):
                delta = new_effect - old_effect
                cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (delta, int(account_id)))
            else:
                cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (-old_effect, old_account_id))
                cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (new_effect, int(account_id)))

            cur.execute(
                "UPDATE transactions SET kind = ?, amount = ?, account_id = ?, tag = ?, note = ?, created_at = ? WHERE id = ?",
                (kind, float(amount), int(account_id), tag, note, tx_date, int(transaction_id)),
            )

    def delete_transaction(self, transaction_id):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT kind, amount, account_id FROM transactions WHERE id = ?", (int(transaction_id),))
            old = cur.fetchone()
            if old is None:
                return

            old_kind, old_amount, old_account_id = old[0], float(old[1]), int(old[2])
            effect = old_amount if old_kind == "Wpłata" else -old_amount
            cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (effect, old_account_id))
            cur.execute("DELETE FROM transactions WHERE id = ?", (int(transaction_id),))

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

    def _parse_date(self, date_str):
        try:
            return datetime.fromisoformat(date_str).date()
        except ValueError:
            return date.today()

    def _next_due_date(self, current_date, frequency):
        if isinstance(current_date, str):
            current_date = self._parse_date(current_date)

        frequency = frequency or "Miesięcznie"
        if frequency == "Codziennie":
            return current_date + timedelta(days=1)
        if frequency == "Co tydzień":
            return current_date + timedelta(days=7)
        if frequency == "Co 2 tygodnie":
            return current_date + timedelta(days=14)
        if frequency == "Co 3 miesiące":
            month_increment = 3
        else:
            month_increment = 1

        month = current_date.month + month_increment
        year = current_date.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        day = min(current_date.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def add_recurring(self, name, kind, amount, account_id, tag, note, frequency, next_date=None):
        if not next_date:
            next_date = str(date.today())
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO recurring_transactions(name, kind, amount, account_id, tag, note, frequency, next_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, kind, float(amount), int(account_id), tag, note, frequency, next_date),
            )
            return cur.lastrowid

    def update_recurring(self, recurring_id, name, kind, amount, account_id, tag, note, frequency, next_date, active=1):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE recurring_transactions SET name = ?, kind = ?, amount = ?, account_id = ?, tag = ?, note = ?, frequency = ?, next_date = ?, active = ? WHERE id = ?",
                (name, kind, float(amount), int(account_id), tag, note, frequency, next_date, int(active), int(recurring_id)),
            )

    def delete_recurring(self, recurring_id):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM recurring_transactions WHERE id = ?", (int(recurring_id),))

    def recurring_transactions(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT r.*, a.name AS account_name
            FROM recurring_transactions r
            JOIN accounts a ON a.id = r.account_id
            ORDER BY r.id DESC
            """
        )
        return [dict(r) for r in cur.fetchall()]

    def process_recurring(self):
        today = date.today()
        templates = self.recurring_transactions()
        if not templates:
            return

        for template in templates:
            if template.get('active') != 1:
                continue

            next_due = self._parse_date(template['next_date'])
            updated_date = next_due
            while updated_date <= today:
                self.add_transaction(
                    template['kind'],
                    template['amount'],
                    template['account_id'],
                    template['tag'],
                    f"Cykliczne: {template['name']}" if template['name'] else template['tag'],
                    tx_date=str(updated_date),
                )
                updated_date = self._next_due_date(updated_date, template['frequency'])

            if str(updated_date) != template['next_date']:
                with self.conn:
                    cur = self.conn.cursor()
                    cur.execute(
                        "UPDATE recurring_transactions SET next_date = ? WHERE id = ?",
                        (str(updated_date), int(template['id'])),
                    )

    def factory_reset(self):
        self.conn.close()
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        self._init_schema()