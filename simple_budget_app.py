import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

DB_DIR = os.path.join("data")
DB_FILE = os.path.join(DB_DIR, "simple_budget.sqlite3")


class SimpleBudgetDB:
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


class AddAccountDialog(tk.Toplevel):
    def __init__(self, parent, on_saved):
        super().__init__(parent)
        self.title("Dodaj konto")
        self.geometry("340x280")
        self.configure(bg="#0F172A")
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="Nowe konto", bg="#0F172A", fg="#F8FAFC", font=("Segoe UI", 16, "bold")).pack(pady=(18, 8))
        tk.Label(self, text="Nazwa konta", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        self.name_entry = tk.Entry(self, bg="#111827", fg="#F8FAFC", insertbackground="#F8FAFC")
        self.name_entry.pack(fill="x", padx=18, pady=(4, 10))

        tk.Label(self, text="Kwota startowa", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        self.balance_entry = tk.Entry(self, bg="#111827", fg="#F8FAFC", insertbackground="#F8FAFC")
        self.balance_entry.pack(fill="x", padx=18, pady=(4, 10))

        self.color_var = tk.StringVar(value="#2563EB")
        tk.Label(self, text="Kolor", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        ttk.Combobox(self, textvariable=self.color_var, values=["#2563EB", "#8B5CF6", "#10B981", "#F59E0B"], state="readonly").pack(fill="x", padx=18, pady=(4, 10))

        tk.Button(self, text="Zapisz konto", bg="#2563EB", fg="#F8FAFC", font=("Segoe UI", 11, "bold"), command=lambda: self._save(on_saved)).pack(pady=12)

    def _save(self, on_saved):
        try:
            name = self.name_entry.get().strip() or "Konto"
            balance = float(self.balance_entry.get().replace(',', '.')) if self.balance_entry.get().strip() else 0.0
            on_saved(name, balance, self.color_var.get())
            self.destroy()
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną kwotę")


class AddTransactionDialog(tk.Toplevel):
    def __init__(self, parent, accounts, tags, on_saved):
        super().__init__(parent)
        self.title("Nowy wpis")
        self.geometry("380x430")
        self.configure(bg="#0F172A")
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="Dodaj wpis", bg="#0F172A", fg="#F8FAFC", font=("Segoe UI", 16, "bold")).pack(pady=(16, 8))

        self.kind_var = tk.StringVar(value="Wypłata")
        tk.Label(self, text="Rodzaj", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        ttk.Combobox(self, textvariable=self.kind_var, values=["Wpłata", "Wypłata"], state="readonly").pack(fill="x", padx=18, pady=(4, 6))

        tk.Label(self, text="Kwota", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        self.amount_entry = tk.Entry(self, bg="#111827", fg="#F8FAFC", insertbackground="#F8FAFC")
        self.amount_entry.pack(fill="x", padx=18, pady=(4, 6))

        self.account_var = tk.StringVar(value=accounts[0]['name'] if accounts else "")
        tk.Label(self, text="Konto", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        ttk.Combobox(self, textvariable=self.account_var, values=[a['name'] for a in accounts] if accounts else ["Brak kont"], state="readonly").pack(fill="x", padx=18, pady=(4, 6))

        self.tag_var = tk.StringVar(value=tags[0]['name'] if tags else "Inne")
        tk.Label(self, text="Tag", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        ttk.Combobox(self, textvariable=self.tag_var, values=[t['name'] for t in tags], state="readonly").pack(fill="x", padx=18, pady=(4, 6))

        tk.Label(self, text="Notatka", bg="#0F172A", fg="#CBD5E1", anchor="w").pack(fill="x", padx=18)
        self.note_entry = tk.Entry(self, bg="#111827", fg="#F8FAFC", insertbackground="#F8FAFC")
        self.note_entry.pack(fill="x", padx=18, pady=(4, 6))

        tk.Button(self, text="Dodaj wpis", bg="#2563EB", fg="#F8FAFC", font=("Segoe UI", 11, "bold"), command=lambda: self._save(accounts, on_saved)).pack(pady=14)

    def _save(self, accounts, on_saved):
        try:
            amount = float(self.amount_entry.get().replace(',', '.'))
            if amount <= 0:
                raise ValueError
            account = next((a for a in accounts if a['name'] == self.account_var.get()), None)
            if account is None:
                raise ValueError("Brak konta")
            on_saved(self.kind_var.get(), amount, account['id'], self.tag_var.get(), self.note_entry.get().strip() or "")
            self.destroy()
        except ValueError:
            messagebox.showerror("Błąd", "Wpisz poprawną kwotę i wybierz konto")


class SimpleBudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Budget iOS")
        self.geometry("430x900")
        self.minsize(380, 760)
        self.configure(bg="#0F172A")
        self.db = SimpleBudgetDB()

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#111827", background="#111827", foreground="#F8FAFC")
        style.map("TCombobox", fieldbackground=[("!disabled", "#111827")], foreground=[("!disabled", "#F8FAFC")])

        top = tk.Frame(self, bg="#0F172A")
        top.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(top, text="Budżet", bg="#0F172A", fg="#F8FAFC", font=("Segoe UI", 24, "bold")).pack(side="left")

        self.view_var = tk.StringVar(value="Main")
        ttk.Combobox(top, textvariable=self.view_var, values=["Main", "Statystyki"], state="readonly", width=14).pack(side="right")
        self.view_var.trace_add("write", lambda *_: self.render())

        self.canvas = tk.Canvas(self, bg="#0F172A", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=(0, 80))

        self.scroll = tk.Frame(self.canvas, bg="#0F172A")
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll, anchor="nw")
        self.canvas.bind("<Configure>", self._on_configure)

        self.fab = tk.Button(self, text="+", bg="#2563EB", fg="#F8FAFC", font=("Segoe UI", 22, "bold"), bd=0, relief="flat", width=4, height=1, command=self.open_add_menu)
        self.fab.place(relx=1.0, rely=1.0, x=-18, y=-18, anchor="se")

        self.render()

    def _on_configure(self, event):
        self.canvas.configure(scrollregion=(0, 0, event.width, self.scroll.winfo_reqheight()))
        self.canvas.itemconfigure(self.scroll_window, width=event.width)

    def render(self):
        for child in self.scroll.winfo_children():
            child.destroy()

        accounts = self.db.accounts()
        total = sum(a['balance'] for a in accounts)

        if self.view_var.get() == "Main":
            tk.Label(self.scroll, text="Łącznie na wszystkich kontach", bg="#0F172A", fg="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=8, pady=(4, 0))
            tk.Label(self.scroll, text=f"{total:.0f} zł", bg="#0F172A", fg="#F8FAFC", font=("Segoe UI", 30, "bold")).pack(anchor="w", padx=8, pady=(2, 12))

            if not accounts:
                empty = tk.Frame(self.scroll, bg="#111827", bd=0)
                empty.pack(fill="x", padx=8, pady=6)
                tk.Label(empty, text="Brak kont — dodaj pierwsze konto", bg="#111827", fg="#CBD5E1", font=("Segoe UI", 13)).pack(pady=18)
                tk.Button(empty, text="Dodaj konto", bg="#2563EB", fg="#F8FAFC", bd=0, font=("Segoe UI", 11, "bold"), command=self.add_account).pack(pady=(0, 16))
            else:
                for account in accounts:
                    card = tk.Frame(self.scroll, bg="#111827", bd=0)
                    card.pack(fill="x", padx=8, pady=6)
                    tk.Label(card, text=account['name'], bg="#111827", fg="#F8FAFC", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
                    tk.Label(card, text=f"{account['balance']:.2f} zł", bg="#111827", fg="#60A5FA", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=14, pady=(0, 12))

                tk.Button(self.scroll, text="Dodaj konto", bg="#2563EB", fg="#F8FAFC", bd=0, font=("Segoe UI", 11, "bold"), command=self.add_account).pack(pady=10)

            history = tk.Frame(self.scroll, bg="#111827", bd=0)
            history.pack(fill="x", padx=8, pady=(14, 6))
            tk.Label(history, text="Historia wpisów", bg="#111827", fg="#F8FAFC", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
            for item in self.db.transactions():
                row = tk.Frame(history, bg="#172033", bd=0)
                row.pack(fill="x", padx=10, pady=4)
                sign = "+" if item['kind'] == "Wpłata" else "-"
                color = "#34D399" if item['kind'] == "Wpłata" else "#F87171"
                tk.Label(row, text=f"{sign} {item['amount']:.0f} zł", bg="#172033", fg=color, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
                tk.Label(row, text=f"{item['account_name']} • {item['tag']} • {item['note'] or 'Brak notatki'}", bg="#172033", fg="#CBD5E1", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(0, 8))
        else:
            tk.Label(self.scroll, text="Statystyki", bg="#0F172A", fg="#F8FAFC", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=8, pady=(4, 8))
            tk.Label(self.scroll, text="Wydatki i wpływy według tagów", bg="#0F172A", fg="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=8, pady=(0, 8))
            for item in self.db.stats():
                card = tk.Frame(self.scroll, bg="#111827", bd=0)
                card.pack(fill="x", padx=8, pady=6)
                tk.Label(card, text=item['tag'], bg="#111827", fg="#F8FAFC", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
                tk.Label(card, text=f"Wydano: {item['spent']:.0f} zł   •   Wpłaty: {item['income']:.0f} zł", bg="#111827", fg="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w", padx=12, pady=(0, 10))

            if not self.db.stats():
                tk.Label(self.scroll, text="Brak danych — dodaj pierwszy wpis", bg="#0F172A", fg="#CBD5E1", font=("Segoe UI", 13)).pack(pady=20)

        self.update_idletasks()
        self.canvas.configure(scrollregion=(0, 0, self.winfo_width(), self.scroll.winfo_reqheight()))

    def add_account(self):
        AddAccountDialog(self, on_saved=self._save_account)

    def _save_account(self, name, balance, color):
        self.db.add_account(name, balance, color)
        self.render()

    def open_add_menu(self):
        accounts = self.db.accounts()
        tags = self.db.tags()
        AddTransactionDialog(self, accounts, tags, on_saved=self._save_transaction)

    def _save_transaction(self, kind, amount, account_id, tag, note):
        self.db.add_transaction(kind, amount, account_id, tag, note)
        self.render()


if __name__ == "__main__":
    app = SimpleBudgetApp()
    app.mainloop()
    app.db.close()
