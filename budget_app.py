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
        self.geometry("1200x900")
        self.minsize(380, 760)
        self.configure(bg="#111217")
        self.db = SimpleBudgetDB()

        #Main/Statystyki
        # style = ttk.Style(self)
        # style.theme_use("clam")
        # style.configure("TCombobox", fieldbackground="#40B5B3", background="transparent", foreground="#F8FAFC")
        # style.map("TCombobox", fieldbackground=[("!disabled", "#111217")], foreground=[("!disabled", "#F8FAFC")])

        #Ramka z nazwa aplikacji
        top = ctk.CTkFrame(self, fg_color="#1B1D29", corner_radius=10)
        top.pack(fill="x", padx=8, pady=(14, 8))
        tk.Label(top, text="BudgetFlow", bg="#1B1D29", fg="#F8FAFC", font=("Segoe UI", 32, "bold")).pack(side="left", padx=20)
        main_btt = ctk.CTkButton(top, text="Statystyki", fg_color="transparent").pack(side="right")
        stat_btt = ctk.CTkButton(top, text="Strona główna", fg_color="transparent").pack(side="right")

        #Main/Statystyki
        self.view_var = tk.StringVar(value="Statystyki")
        ttk.Combobox(top, textvariable=self.view_var, values=["Main", "Statystyki"], state="readonly", width=14).pack(side="right")
        self.view_var.trace_add("write", lambda *_: self.render())

        main_btt = ctk.CTkButton(top, text="Statystyki", fg_color="transparent", command=lambda: ).pack(side="right")
        stat_btt = ctk.CTkButton(top, text="Strona główna", fg_color="transparent").pack(side="right")


        #???
        self.canvas = tk.Canvas(self, bg="#111217", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=(0, 0))

        #Ramka body
        self.scroll = ctk.CTkFrame(self.canvas, fg_color="#1B1D29", corner_radius=10)
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll, anchor="nw")
        self.canvas.bind("<Configure>", self._on_configure)

        #Przycisk do dodwania wpisow
        self.fab = ctk.CTkButton(self, text="+", fg_color="#6E5BE8", font=("Segoe UI", 24, "bold"), width=50, height=50, corner_radius=10, command=self.open_add_menu)
        self.fab.place(relx=1.0, rely=1.0, x=-36, y=-18, anchor="se")
        self.fab.lift()
        self.render()

    def _on_configure(self, event):
        req_height = self.scroll.winfo_reqheight()
        height = max(event.height, req_height)
        self.canvas.configure(scrollregion=(0, 0, event.width, req_height))
        self.canvas.itemconfigure(self.scroll_window, width=event.width, height=height)

    def render(self):
        for child in self.scroll.winfo_children():
            child.destroy()

        accounts = self.db.accounts()
        total = sum(a['balance'] for a in accounts)

        if self.view_var.get() == "Main":
            body_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
            body_frame.pack(fill="both", padx=8, pady=4, expand=True)
            body_frame.grid_columnconfigure(0, weight=1, uniform="group1")
            body_frame.grid_columnconfigure(1, weight=1, uniform="group1")
            body_frame.grid_rowconfigure(0, weight=1)

            body_left = ctk.CTkScrollableFrame(body_frame, fg_color="transparent", label_text="")
            body_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

            tk.Label(body_left, text="Łącznie na wszystkich kontach", bg="#1B1D29", fg="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=8, pady=(4, 0))
            tk.Label(body_left, text=f"{total:.0f} zł", bg="#1B1D29", fg="#F8FAFC", font=("Segoe UI", 30, "bold")).pack(anchor="w", padx=8, pady=(2, 12))

            if not accounts:
                empty = ctk.CTkFrame(self.scroll, fg_color="#252837", corner_radius=10)
                empty.pack(fill="x", padx=8, pady=6)
                tk.Label(empty, text="Brak kont — dodaj pierwsze konto", bg="#111217", fg="#CBD5E1", font=("Segoe UI", 13)).pack(pady=18)
                ctk.CTkButton(self.scroll, text="Dodaj konto", fg_color="#6E5BE8", font=("Segoe UI", 14, "bold"), corner_radius=10, command=self.add_account).pack(pady=10)
            else:
                for account in accounts:
                    card = ctk.CTkFrame(body_left, fg_color="#252837", corner_radius=10)
                    card.pack(fill="x", padx=8, pady=6)
                    tk.Label(card, text=account['name'], bg="#252837", fg="#F8FAFC", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
                    tk.Label(card, text=f"{account['balance']:.2f} zł", bg="#252837", fg="#a095e8", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=14, pady=(0, 12))

                #Przycisk dodaj konto
                ctk.CTkButton(body_left, text="Dodaj konto", fg_color="#6E5BE8", font=("Segoe UI", 14, "bold"), corner_radius=10, command=self.add_account).pack(pady=10)

            body_right = ctk.CTkScrollableFrame(body_frame, fg_color="transparent")
            body_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

            history = ctk.CTkFrame(body_right, fg_color="#111217", corner_radius=10)
            history.pack(fill="both", padx=8, pady=(8, 8), expand=True)
            tk.Label(history, text="Historia wpisów", bg="#111217", fg="#F8FAFC", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
            for item in self.db.transactions():
                row = ctk.CTkFrame(history, fg_color="#252837", corner_radius=10)
                row.pack(fill="x", padx=10, pady=4)
                sign = "+" if item['kind'] == "Wpłata" else "-"
                color = "#95e8af" if item['kind'] == "Wpłata" else "#e89595"
                tk.Label(row, text=f"{sign} {item['amount']:.0f} zł", bg="#252837", fg=color, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
                tk.Label(row, text=f"{item['account_name']} • {item['tag']} • {item['note'] or 'Brak notatki'}", bg="#252837", fg="#CBD5E1", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(0, 8))
        else:
            #Zakladka statystyki
            stat_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
            stat_frame.pack(fill="both", padx=8, pady=4, expand=True)
            stat_frame.grid_columnconfigure(0, weight=1, uniform="group2")
            stat_frame.grid_columnconfigure(1, weight=1, uniform="group2")
            stat_frame.grid_columnconfigure(2, weight=1, uniform="group2")
            stat_frame.grid_rowconfigure(0, weight=1)

            tk.Label(self.scroll, text="Statystyki", bg="#1B1D29", fg="#F8FAFC", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=8, pady=(4, 8))
            tk.Label(self.scroll, text="Wydatki i wpływy według tagów", bg="#1B1D29", fg="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=8, pady=(0, 8))
            stats = self.db.stats()
            for item in stats:
                card = ctk.CTkFrame(self.scroll, fg_color="#252837", corner_radius=10)
                card.pack(fill="x", padx=8, pady=6)
                tk.Label(card, text=item['tag'], bg="#252837", fg="#F8FAFC", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
                tk.Label(card, text=f"Wydano: {item['spent']:.0f} zł   •   Wpłaty: {item['income']:.0f} zł", bg="#252837", fg="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w", padx=12, pady=(0, 10))

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
