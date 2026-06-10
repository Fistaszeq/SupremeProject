"""
Moduł głównej aplikacji GUI.

Edytorzy:
- tutaj zmieniaj układ ekranu, widok Main/Statystyki i przyciski,
- logika bazy jest w budget_db.py, a formularze w budget_dialogs.py.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from budget_db import SimpleBudgetDB
from budget_dialogs import AddAccountDialog, AddTransactionDialog


class SimpleBudgetApp(tk.Tk):
    """Główna klasa aplikacji budżetowej."""

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
            stats = self.db.stats()
            for item in stats:
                card = tk.Frame(self.scroll, bg="#111827", bd=0)
                card.pack(fill="x", padx=8, pady=6)
                tk.Label(card, text=item['tag'], bg="#111827", fg="#F8FAFC", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
                tk.Label(card, text=f"Wydano: {item['spent']:.0f} zł   •   Wpłaty: {item['income']:.0f} zł", bg="#111827", fg="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w", padx=12, pady=(0, 10))

            if not stats:
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
