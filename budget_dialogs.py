"""
Moduł formularzy i okien dialogowych.

Edytorzy:
- tutaj zmieniaj wygląd okien, etykiety i walidację wejść,
- nie dodawaj logiki biznesowej do tego pliku.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class AddAccountDialog(tk.Toplevel):
    """Okno dodawania nowego konta."""

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
            balance = float(self.balance_entry.get().replace(",", ".")) if self.balance_entry.get().strip() else 0.0
            on_saved(name, balance, self.color_var.get())
            self.destroy()
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną kwotę")


class AddTransactionDialog(tk.Toplevel):
    """Okno dodawania wpisu wydatku/ wpłaty."""

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
            amount = float(self.amount_entry.get().replace(",", "."))
            if amount <= 0:
                raise ValueError
            account = next((a for a in accounts if a['name'] == self.account_var.get()), None)
            if account is None:
                raise ValueError("Brak konta")
            on_saved(self.kind_var.get(), amount, account['id'], self.tag_var.get(), self.note_entry.get().strip() or "")
            self.destroy()
        except ValueError:
            messagebox.showerror("Błąd", "Wpisz poprawną kwotę i wybierz konto")
