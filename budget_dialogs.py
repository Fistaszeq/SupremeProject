"""
Moduł formularzy i okien dialogowych w stylu iOS Design.
"""

import tkinter as tk
from tkinter import messagebox, colorchooser
import customtkinter as ctk
from datetime import date

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AccountDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_saved, account=None):
        super().__init__(parent)
        self.is_edit = account is not None
        self.account_id = account['id'] if self.is_edit else None
        
        # Pobieranie czcionki dziedziczonej ze środowiska aplikacji 
        self.app_font = parent.db.get_font() if hasattr(parent, 'db') else "Segoe UI"
        
        self.title("Edytuj konto" if self.is_edit else "Dodaj konto")
        self.geometry("360x420")
        self.configure(fg_color="#1C1C1E")
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.resizable(False, False)

        title_text = "Edycja konta" if self.is_edit else "Nowe konto"
        ctk.CTkLabel(self, text=title_text, text_color="#FFFFFF", font=(self.app_font, 20, "bold")).pack(pady=(20, 15))
        
        ctk.CTkLabel(self, text="NAZWA KONTA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.name_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, placeholder_text="np. Gotówka", font=(self.app_font, 12))
        self.name_entry.pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkLabel(self, text="KWOTA (SALDO)", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.balance_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, placeholder_text="0.00", font=(self.app_font, 12))
        self.balance_entry.pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkLabel(self, text="KOLOR IDENTYFIKACYJNY", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        
        self.color_map = {
            "Niebieski": "#2563EB",
            "Fioletowy": "#8B5CF6",
            "Zielony": "#10B981",
            "Bursztynowy": "#F59E0B",
            "Własny...": "custom"
        }
        self.reverse_color_map = {v: k for k, v in self.color_map.items()}
        
        self.selected_hex = ctk.StringVar()
        self.display_color_var = ctk.StringVar()

        self.color_combo = ctk.CTkComboBox(
            self, 
            variable=self.display_color_var, 
            values=list(self.color_map.keys()), 
            fg_color="#2C2C2E", 
            border_color="#3A3A3C", 
            button_color="#3A3A3C", 
            text_color="#FFFFFF", 
            corner_radius=10, 
            state="readonly",
            command=self._on_color_select,
            font=(self.app_font, 12)
        )
        self.color_combo.pack(fill="x", padx=24, pady=(4, 16))

        if self.is_edit:
            self.name_entry.insert(0, account['name'])
            self.balance_entry.insert(0, str(account['balance']))
            
            hex_val = account['color']
            self.selected_hex.set(hex_val)
            if hex_val in self.reverse_color_map:
                self.display_color_var.set(self.reverse_color_map[hex_val])
            else:
                new_display = f"Własny ({hex_val})"
                self.display_color_var.set(new_display)
                updated_values = list(self.color_map.keys())[:-1] + [new_display, "Własny..."]
                self.color_combo.configure(values=updated_values)
        else:
            self.selected_hex.set("#2563EB")
            self.display_color_var.set("Niebieski")

        btn_text = "Zapisz zmiany" if self.is_edit else "Zapisz konto"
        self.save_btn = ctk.CTkButton(self, text=btn_text, fg_color="#0A84FF", hover_color="#0066CC", text_color="#FFFFFF", font=(self.app_font, 14, "bold"), corner_radius=10, height=40, command=lambda: self._save(on_saved))
        self.save_btn.pack(fill="x", padx=24, pady=20)

        self.bind('<Return>', lambda event: self._save(on_saved))

    def _on_color_select(self, choice):
        if choice == "Własny...":
            color_code = colorchooser.askcolor(title="Wybierz kolor")[1]
            if color_code:
                self.selected_hex.set(color_code)
                new_display = f"Własny ({color_code})"
                self.display_color_var.set(new_display)
                current_values = self.color_combo.cget("values")
                if new_display not in current_values:
                    updated_values = list(self.color_map.keys())[:-1] + [new_display, "Własny..."]
                    self.color_combo.configure(values=updated_values)
            else:
                fallback = self.reverse_color_map.get(self.selected_hex.get(), "Niebieski")
                self.display_color_var.set(fallback)
        else:
            if choice in self.color_map:
                self.selected_hex.set(self.color_map[choice])

    def _save(self, on_saved):
        try:
            name = self.name_entry.get().strip() or "Konto"
            balance = float(self.balance_entry.get().replace(",", ".")) if self.balance_entry.get().strip() else 0.0
            on_saved(self.account_id, name, balance, self.selected_hex.get())
            self.destroy()
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną kwotę")


class AddTransactionDialog(ctk.CTkToplevel):
    def __init__(self, parent, accounts, tags, on_saved, transaction=None):
        super().__init__(parent)
        self.accounts = accounts
        self.current_kind = "Wypłata"
        self.app_font = parent.db.get_font() if hasattr(parent, 'db') else "Segoe UI"
        
        self.title("Nowy wpis")
        self.geometry("380x580")
        self.configure(fg_color="#1C1C1E") 
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Dodaj wpis", text_color="#FFFFFF", font=(self.app_font, 20, "bold")).pack(pady=(20, 15))

        ctk.CTkLabel(self, text="RODZAJ TRANSAKCJI", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        
        self.type_frame = ctk.CTkFrame(self, fg_color="#2C2C2E", corner_radius=8)
        self.type_frame.pack(fill="x", padx=24, pady=(4, 14))
        self.type_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_wyplata = ctk.CTkButton(self.type_frame, text="Wypłata", fg_color="#FF3B30", hover_color="#D73229", text_color="#FFFFFF", font=(self.app_font, 12, "bold"), corner_radius=6, command=lambda: self.set_type("Wypłata"))
        self.btn_wyplata.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.btn_wplata = ctk.CTkButton(self.type_frame, text="Wpłata", fg_color="transparent", hover_color="#3A3A3C", text_color="#8E8E93", font=(self.app_font, 12, "bold"), corner_radius=6, command=lambda: self.set_type("Wpłata"))
        self.btn_wplata.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ctk.CTkLabel(self, text="KWOTA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.amount_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#FF3B30", text_color="#FFFFFF", corner_radius=10, placeholder_text="0.00", font=(self.app_font, 16))
        self.amount_entry.pack(fill="x", padx=24, pady=(4, 14))

        ctk.CTkLabel(self, text="KONTO BAZOWE", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.account_var = ctk.StringVar(value=accounts[0]['name'] if accounts else "")
        self.account_combo = ctk.CTkComboBox(self, variable=self.account_var, values=[a['name'] for a in accounts] if accounts else ["Brak kont"], fg_color="#2C2C2E", border_color="#3A3A3C", button_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, state="readonly", font=(self.app_font, 12))
        self.account_combo.pack(fill="x", padx=24, pady=(4, 14))

        ctk.CTkLabel(self, text="KATEGORIA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        filtered_tags = [t['name'] for t in tags if t['name'] != "Przelew"]
        self.tag_var = ctk.StringVar(value=filtered_tags[0] if filtered_tags else "Inne")
        self.tag_combo = ctk.CTkComboBox(self, variable=self.tag_var, values=filtered_tags, fg_color="#2C2C2E", border_color="#3A3A3C", button_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, state="readonly", font=(self.app_font, 12))
        self.tag_combo.pack(fill="x", padx=24, pady=(4, 14))
        
        ctk.CTkLabel(self, text="DATA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.date_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, placeholder_text="RRRR-MM-DD", font=(self.app_font, 12))
        self.date_entry.pack(fill="x", padx=24, pady=(4, 14))

        ctk.CTkLabel(self, text="NOTATKA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.note_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, placeholder_text="Opcjonalny opis transakcji...", font=(self.app_font, 12))
        self.note_entry.pack(fill="x", padx=24, pady=(4, 20))

        self.save_btn = ctk.CTkButton(self, text="Dodaj wpis", fg_color="#FF3B30", hover_color="#D73229", font=(self.app_font, 14, "bold"), corner_radius=10, height=44, command=lambda: self._save(on_saved))
        self.save_btn.pack(fill="x", padx=24, pady=10)
        
        self.bind('<Return>', lambda event: self._save(on_saved))

        if transaction:
            self.amount_entry.insert(0, str(transaction['amount']))
            self.account_var.set(transaction['account_name'])
            self.tag_var.set(transaction['tag'])
            self.note_entry.insert(0, transaction['note'])
            self.date_entry.insert(0, transaction['created_at'])
            self.set_type(transaction['kind'])
        else:
            self.date_entry.insert(0, str(date.today()))
            self.set_type("Wypłata")

    def set_type(self, kind):
        self.current_kind = kind
        if kind == "Wpłata":
            self.btn_wplata.configure(fg_color="#34C759", text_color="#FFFFFF")
            self.btn_wyplata.configure(fg_color="transparent", text_color="#8E8E93")
            self.save_btn.configure(fg_color="#34C759", hover_color="#2EAC4E")
            self.amount_entry.configure(border_color="#34C759")
        else:
            self.btn_wyplata.configure(fg_color="#FF3B30", text_color="#FFFFFF")
            self.btn_wplata.configure(fg_color="transparent", text_color="#8E8E93")
            self.save_btn.configure(fg_color="#FF3B30", hover_color="#D73229")
            self.amount_entry.configure(border_color="#FF3B30")

    def _save(self, on_saved):
        try:
            amount_str = self.amount_entry.get().replace(",", ".")
            if not amount_str:
                raise ValueError("Kwota nie może być pusta.")
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Kwota musi być większa od zera.")
            account = next((a for a in self.accounts if a['name'] == self.account_var.get()), None)
            if account is None:
                raise ValueError("Brak konta")
                
            tx_date = self.date_entry.get().strip() or str(date.today())
            note = self.note_entry.get().strip() or ""
            
            on_saved(self.current_kind, amount, account['id'], self.tag_var.get(), note, tx_date)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Błąd walidacji", f"Nieprawidłowe dane: {str(e)}")


class TransferDialog(ctk.CTkToplevel):
    def __init__(self, parent, accounts, on_saved):
        super().__init__(parent)
        self.accounts = accounts
        self.app_font = parent.db.get_font() if hasattr(parent, 'db') else "Segoe UI"
        
        self.title("Przelew środków")
        self.geometry("380x520")
        self.configure(fg_color="#1C1C1E") 
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Przelew między kontami", text_color="#FFFFFF", font=(self.app_font, 20, "bold")).pack(pady=(20, 15))

        ctk.CTkLabel(self, text="Z KONTA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.from_account_var = ctk.StringVar(value=accounts[0]['name'] if accounts else "")
        self.from_account_combo = ctk.CTkComboBox(self, variable=self.from_account_var, values=[a['name'] for a in accounts], fg_color="#2C2C2E", border_color="#3A3A3C", button_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, state="readonly", font=(self.app_font, 12))
        self.from_account_combo.pack(fill="x", padx=24, pady=(4, 14))

        ctk.CTkLabel(self, text="NA KONTO", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        to_initial = accounts[1]['name'] if len(accounts) > 1 else accounts[0]['name']
        self.to_account_var = ctk.StringVar(value=to_initial)
        self.to_account_combo = ctk.CTkComboBox(self, variable=self.to_account_var, values=[a['name'] for a in accounts], fg_color="#2C2C2E", border_color="#3A3A3C", button_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, state="readonly", font=(self.app_font, 12))
        self.to_account_combo.pack(fill="x", padx=24, pady=(4, 14))

        ctk.CTkLabel(self, text="KWOTA PRZELEWU", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.amount_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#8B5CF6", text_color="#FFFFFF", corner_radius=10, placeholder_text="0.00", font=(self.app_font, 16))
        self.amount_entry.pack(fill="x", padx=24, pady=(4, 14))

        ctk.CTkLabel(self, text="DATA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.date_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, placeholder_text="RRRR-MM-DD", font=(self.app_font, 12))
        self.date_entry.pack(fill="x", padx=24, pady=(4, 14))
        self.date_entry.insert(0, str(date.today()))

        ctk.CTkLabel(self, text="NOTATKA", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24)
        self.note_entry = ctk.CTkEntry(self, fg_color="#2C2C2E", border_color="#3A3A3C", text_color="#FFFFFF", corner_radius=10, placeholder_text="Opcjonalny opis...", font=(self.app_font, 12))
        self.note_entry.pack(fill="x", padx=24, pady=(4, 20))

        self.save_btn = ctk.CTkButton(self, text="Wykonaj przelew", fg_color="#8B5CF6", hover_color="#7C3AED", font=(self.app_font, 14, "bold"), corner_radius=10, height=44, command=lambda: self._save(on_saved))
        self.save_btn.pack(fill="x", padx=24, pady=10)
        
        self.bind('<Return>', lambda event: self._save(on_saved))

    def _save(self, on_saved):
        try:
            from_name = self.from_account_var.get()
            to_name = self.to_account_var.get()
            
            if from_name == to_name:
                raise ValueError("Konto docelowe musi być inne niż źródłowe.")
                
            amount_str = self.amount_entry.get().replace(",", ".")
            if not amount_str:
                raise ValueError("Kwota nie może być pusta.")
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Kwota musi być większa od zera.")
                
            from_account = next((a for a in self.accounts if a['name'] == from_name), None)
            to_account = next((a for a in self.accounts if a['name'] == to_name), None)
            
            if from_account is None or to_account is None:
                raise ValueError("Brak konta")
                
            tx_date = self.date_entry.get().strip() or str(date.today())
            note = self.note_entry.get().strip() or ""
            
            on_saved(from_account['id'], to_account['id'], amount, note, tx_date)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Błąd walidacji", f"Nieprawidłowe dane: {str(e)}")


class AccountDetailsDialog(ctk.CTkToplevel):
    def __init__(self, parent, account, db, currency="zł"):
        super().__init__(parent)
        self.app_font = parent.db.get_font() if hasattr(parent, 'db') else "Segoe UI"
        
        self.title(f"Analityka: {account['name']}")
        self.geometry("460x620")
        self.configure(fg_color="#1C1C1E")
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.resizable(False, False)

        ctk.CTkLabel(self, text=account['name'].upper(), text_color="#8E8E93", font=(self.app_font, 12, "bold")).pack(pady=(22, 2))
        ctk.CTkLabel(self, text=f"{account['balance']:.2f} {currency}", text_color="#FFFFFF", font=(self.app_font, 28, "bold")).pack(pady=(0, 15))

        stats = db.account_stats(account['id'])
        spent_stats = [s for s in stats if s['spent'] > 0]

        if not spent_stats:
            ctk.CTkLabel(self, text="STRUKTURA WYDATKÓW", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24, pady=(10, 5))
            self.no_data_frame = ctk.CTkFrame(self, fg_color="#2C2C2E", corner_radius=12)
            self.no_data_frame.pack(fill="both", expand=True, padx=24, pady=10)
            ctk.CTkLabel(self.no_data_frame, text="Brak wydatków na tym koncie.\nDodaj transakcję typu 'Wypłata',\naby wygenerować wykres graficzny.", text_color="#AEAEB2", font=(self.app_font, 13)).pack(expand=True, pady=20)
        else:
            ctk.CTkLabel(self, text="STRUKTURA WYDATKÓW (PODZIAŁ NA TAGI)", text_color="#8E8E93", font=(self.app_font, 11, "bold"), anchor="w").pack(fill="x", padx=24, pady=(10, 5))

            tags = [s['tag'] for s in spent_stats]
            amounts = [s['spent'] for s in spent_stats]

            fig = Figure(figsize=(4.5, 3.5), facecolor='#1C1C1E')
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1C1C1E')

            ios_colors = ['#FF3B30', '#FF9500', '#FFCC00', '#34C759', '#5AC8FA', '#007AFF', '#5856D6', '#AF52DE']
            
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=tags, 
                autopct='%1.0f%%', 
                startangle=140, 
                colors=ios_colors[:len(tags)],
                textprops=dict(color="#FFFFFF", size=11, fontname=self.app_font), 
                wedgeprops=dict(width=0.35, edgecolor='#1C1C1E', linewidth=2) 
            )

            for autotext in autotexts:
                autotext.set_color('#FFFFFF')
                autotext.set_weight('bold')
                autotext.set_size(10)

            ax.axis('equal')  
            
            canvas = FigureCanvasTkAgg(fig, master=self)
            
            fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

            canvas_widget = canvas.get_tk_widget()
            canvas_widget.configure(bg='#1C1C1E', highlightthickness=0)
            canvas_widget.pack(fill="both", expand=True, padx=24, pady=5)
            canvas.draw()

        ctk.CTkButton(self, text="Gotowe", fg_color="#3A3A3C", hover_color="#48484A", text_color="#FFFFFF", font=(self.app_font, 14, "bold"), corner_radius=10, height=42, command=self.destroy).pack(fill="x", padx=24, pady=(10, 35))