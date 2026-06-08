"""
Moduł bazy danych dla aplikacji budżetowej.

Edytorzy:
- tutaj zmieniaj schemat tabel, domyślne tagi i logikę zapisów/odczytów,
- nie modyfikuj kodu GUI w tym pliku.
"""

import os
import sqlite3
from datetime import date

DB_DIR = os.path.join("data")
DB_FILE = os.path.join(DB_DIR, "simple_budget.sqlite3")


class SimpleBudgetDB:
    """Warstwa dostępu do bazy SQLite.

    Odpowiada za tworzenie tabel, zapis kont i transakcji oraz pobieranie statystyk.
    """

    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
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
                created_at TEXT NOT NULL DEFAULT CURRENT_DATE
            );
            """
        )
        self.conn.commit()

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
            self.conn.commit()

    def close(self):
        self.conn.close()

    def accounts(self):
        return [dict(r) for r in self.conn.execute("SELECT * FROM accounts ORDER BY id")]

    def add_account(self, name, balance, color):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO accounts(name, balance, color) VALUES (?, ?, ?)", (name, float(balance), color))
        self.conn.commit()
        return cur.lastrowid

    def add_transaction(self, kind, amount, account_id, tag, note):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO transactions(kind, amount, account_id, tag, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (kind, float(amount), int(account_id), tag, note, str(date.today())),
        )
        if kind == "Wpłata":
            cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (float(amount), int(account_id)))
        else:
            cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (float(amount), int(account_id)))
        self.conn.commit()
        return cur.lastrowid

    def transactions(self):
        return [dict(r) for r in self.conn.execute(
            """
            SELECT t.*, a.name AS account_name
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            ORDER BY t.id DESC
            LIMIT 20
            """
        )]

    def tags(self):
        return [dict(r) for r in self.conn.execute("SELECT * FROM tags ORDER BY id")]

    def stats(self):
        rows = self.conn.execute(
            """
            SELECT tag,
                   SUM(CASE WHEN kind='Wypłata' THEN amount ELSE 0 END) AS spent,
                   SUM(CASE WHEN kind='Wpłata' THEN amount ELSE 0 END) AS income
            FROM transactions
            GROUP BY tag
            ORDER BY spent DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
