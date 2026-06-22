"""
Moduł głównej aplikacji GUI. Zoptymalizowany.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from budget_db import SimpleBudgetDB
from budget_dialogs import AccountDialog, AddTransactionDialog, AccountDetailsDialog, TransferDialog


class SimpleBudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget iOS")
        self.geometry("1200x900")
        self.minsize(380, 760)
        self.configure(fg_color=("#F3F4F6", "#111217"))
        self.db = SimpleBudgetDB()

        self.app_font = self.db.get_font()

        top = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#1B1D29"), corner_radius=10)
        top.pack(fill="x", padx=8, pady=(14, 8))
        ctk.CTkLabel(top, text="BudgetFlow", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 32, "bold")).pack(side="left", padx=20, pady=10)

        self.view_var = "Main"

        ctk.CTkButton(top, text="Ustawienia", fg_color="transparent", hover_color=("#E5E7EB", "#111217"), text_color=("#111827", "#F8FAFC"), font=(self.app_font, 14, "bold"), command=lambda: self.switch_view("Ustawienia")).pack(side="right", padx=(4, 8))
        ctk.CTkButton(top, text="Statystyki", fg_color="transparent", hover_color=("#E5E7EB", "#111217"), text_color=("#111827", "#F8FAFC"), font=(self.app_font, 14, "bold"), command=lambda: self.switch_view("Statystyki")).pack(side="right", padx=(4, 4))
        ctk.CTkButton(top, text="Strona główna", fg_color="transparent", hover_color=("#E5E7EB", "#111217"), text_color=("#111827", "#F8FAFC"), font=(self.app_font, 14, "bold"), command=lambda: self.switch_view("Main")).pack(side="right", padx=(4, 4))

        self.main_container = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#1B1D29"), corner_radius=10)
        self.main_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.frames = {
            "Main": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Statystyki": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Ustawienia": ctk.CTkFrame(self.main_container, fg_color="transparent")
        }
        
        self.loading_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.loading_spinner = ctk.CTkLabel(self.loading_frame, text="Ładowanie danych...", text_color=("#6B7280", "#8E8E93"), font=(self.app_font, 20, "bold"))
        self.loading_spinner.place(relx=0.5, rely=0.5, anchor="center")

        self.fab = ctk.CTkButton(self, text="+", fg_color="#6E5BE8", text_color="#FFFFFF", font=(self.app_font, 24, "bold"), width=50, height=50, corner_radius=10, command=self.open_add_menu)
        self.fab.place(relx=1.0, rely=1.0, x=-36, y=-18, anchor="se")
        self.fab.lift()

        self.trigger_render()

    @staticmethod
    def get_contrast_text_color(hex_color):
        """W3C algorytm luminancji do oceny kontrastu tekstu."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return "#FFFFFF"
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            luminance = (r * 0.299 + g * 0.587 + b * 0.114)
            return "#000000" if luminance > 160 else "#FFFFFF"
        except ValueError:
            return "#FFFFFF"

    def switch_view(self, view_name):
        if self.view_var == view_name:
            return
        self.view_var = view_name
        self.trigger_render()

    def trigger_render(self):
        self.app_font = self.db.get_font()
        for frame in self.frames.values():
            frame.pack_forget()
        
        self.loading_frame.pack(fill="both", expand=True)
        self.update_idletasks() 
        self.after(50, self._execute_render)

    def _execute_render(self):
        self.render()
        self.loading_frame.pack_forget()
        self.frames[self.view_var].pack(fill="both", expand=True)

    def render(self):
        current_frame = self.frames[self.view_var]
        
        for child in current_frame.winfo_children():
            child.destroy()

        accounts = self.db.accounts()
        total = sum(a['balance'] for a in accounts)
        color_family = {"#2563EB": "#1E3A8A", "#8B5CF6": "#4C1D95", "#10B981": "#064E3B", "#F59E0B": "#78350F"}
        currency = self.db.get_currency()

        if self.view_var == "Main":
            current_frame.grid_columnconfigure(0, weight=1, uniform="group1")
            current_frame.grid_columnconfigure(1, weight=1, uniform="group1")
            current_frame.grid_rowconfigure(0, weight=1)

            body_left = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            body_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

            ctk.CTkLabel(body_left, text="Łącznie na wszystkich kontach", text_color=("#4B5563", "#94A3B8"), font=(self.app_font, 13)).pack(anchor="w", padx=8, pady=(4, 0))
            ctk.CTkLabel(body_left, text=f"{total:.2f} {currency}", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 32, "bold")).pack(anchor="w", padx=8, pady=(2, 12))

            if not accounts:
                empty = ctk.CTkFrame(body_left, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
                empty.pack(fill="x", padx=8, pady=6)
                ctk.CTkLabel(empty, text="Brak kont — dodaj pierwsze konto", text_color=("#4B5563", "#CBD5E1"), font=(self.app_font, 14)).pack(pady=18)
            else:
                for account in accounts:
                    card_bg = color_family.get(account['color'], account['color'])
                    text_col = self.get_contrast_text_color(card_bg)
                    subtext_col = "#374151" if text_col == "#000000" else "#E5E7EB"

                    card = ctk.CTkFrame(body_left, fg_color=card_bg, corner_radius=12)
                    card.pack(fill="x", padx=8, pady=6)
                    
                    ctk.CTkLabel(card, text=account['name'], text_color=text_col, font=(self.app_font, 16, "bold")).pack(anchor="w", padx=16, pady=(12, 0))
                    ctk.CTkLabel(card, text=f"{account['balance']:.2f} {currency}", text_color=text_col, font=(self.app_font, 22, "bold")).pack(anchor="w", padx=16, pady=(0, 2))
                    
                    if account['last_date']:
                        sign = "+" if account['last_kind'] == "Wpłata" else "-"
                        last_info = f"Ostatnio: {account['last_date']} ({sign}{account['last_amount']:.2f} {currency})"
                    else:
                        last_info = "Ostatnio: Brak transakcji"
                        
                    ctk.CTkLabel(card, text=last_info, text_color=subtext_col, font=(self.app_font, 11)).pack(anchor="w", padx=16, pady=(0, 10))
                    
                    btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                    btn_frame.pack(anchor="w", padx=16, pady=(0, 12))
                    ctk.CTkButton(btn_frame, text="Szczegóły", width=75, height=24, fg_color="#0A84FF", hover_color="#0066CC", text_color="#FFFFFF", font=(self.app_font, 11, "bold"), command=lambda a=account: self.show_account_details(a)).pack(side="left", padx=(0, 8))
                    ctk.CTkButton(btn_frame, text="Edytuj", width=65, height=24, fg_color="#334155", hover_color="#475569", text_color="#F8FAFC", font=(self.app_font, 11, "bold"), command=lambda a=account: self.edit_account(a)).pack(side="left", padx=(0, 8))
                    ctk.CTkButton(btn_frame, text="Usuń", width=65, height=24, fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF", font=(self.app_font, 11, "bold"), command=lambda a=account: self.delete_account(a)).pack(side="left")

            buttons_frame = ctk.CTkFrame(body_left, fg_color="transparent")
            buttons_frame.pack(fill="x", pady=10)
            ctk.CTkButton(buttons_frame, text="Dodaj konto", fg_color="#6E5BE8", text_color="#FFFFFF", font=(self.app_font, 14, "bold"), corner_radius=10, command=self.add_account).pack(side="left", expand=True, padx=4)
            ctk.CTkButton(buttons_frame, text="Przelew", fg_color="#8B5CF6", text_color="#FFFFFF", font=(self.app_font, 14, "bold"), corner_radius=10, command=self.open_transfer_menu).pack(side="left", expand=True, padx=4)

            body_right = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            body_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

            history = ctk.CTkFrame(body_right, fg_color=("#F3F4F6", "#111217"), corner_radius=10)
            history.pack(fill="both", padx=8, pady=(8, 8), expand=True)
            ctk.CTkLabel(history, text="Historia wpisów", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 16, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
            
            for item in self.db.transactions():
                row = ctk.CTkFrame(history, fg_color=("#FFFFFF", "#252837"), corner_radius=10)
                row.pack(fill="x", padx=10, pady=6)
                
                top_row = ctk.CTkFrame(row, fg_color="transparent")
                top_row.pack(fill="x", padx=14, pady=(12, 2))
                
                title_text = item['note'] if item['note'] else item['tag']
                ctk.CTkLabel(top_row, text=title_text, text_color=("#111827", "#F8FAFC"), font=(self.app_font, 15, "bold")).pack(side="left")
                
                sign = "+" if item['kind'] == "Wpłata" else "-"
                status_color = "#34C759" if item['kind'] == "Wpłata" else "#FF3B30"
                if item['tag'] == "Przelew":
                    status_color = "#8B5CF6"
                    
                ctk.CTkLabel(top_row, text=f"{sign} {item['amount']:.2f} {currency}", text_color=status_color, font=(self.app_font, 15, "bold")).pack(side="right")
                
                bottom_row = ctk.CTkFrame(row, fg_color="transparent")
                bottom_row.pack(fill="x", padx=14, pady=(0, 12))
                
                meta_text = f"{item['created_at']} • {item['account_name']} • {item['tag']}"
                ctk.CTkLabel(bottom_row, text=meta_text, text_color=("#6B7280", "#94A3B8"), font=(self.app_font, 12)).pack(side="left", pady=(2, 0))
                
                if item['tag'] != "Przelew":
                    ctk.CTkButton(bottom_row, text="Ponów", width=60, height=24, fg_color=("#E5E7EB", "#3A3A3C"), hover_color=("#D1D5DB", "#48484A"), text_color=("#111827", "#FFFFFF"), font=(self.app_font, 11, "bold"), corner_radius=6, command=lambda t=item: self.repeat_transaction(t)).pack(side="right")

        elif self.view_var == "Statystyki":
            stat_scroll = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            stat_scroll.pack(fill="both", expand=True)

            ctk.CTkLabel(stat_scroll, text="Statystyki Globalne", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 24, "bold")).pack(anchor="w", padx=20, pady=(10, 20))
            
            stats = self.db.stats()
            total_spent = sum(s['spent'] for s in stats)
            total_income = sum(s['income'] for s in stats)
            max_category = stats[0]['tag'] if stats and stats[0]['spent'] > 0 else "Brak wydatków"

            # 1. Kafelki podsumowujące (Góra)
            summary_frame = ctk.CTkFrame(stat_scroll, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
            summary_frame.pack(fill="x", padx=20, pady=(0, 15))
            summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

            ctk.CTkLabel(summary_frame, text="Saldo wszystkich kont", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 11, "bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(summary_frame, text="Łączne wydatki", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 11, "bold")).grid(row=0, column=1, sticky="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(summary_frame, text="Łączne przychody", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 11, "bold")).grid(row=0, column=2, sticky="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(summary_frame, text="Aktywne cykliczne", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 11, "bold")).grid(row=0, column=3, sticky="w", padx=20, pady=(15, 5))

            ctk.CTkLabel(summary_frame, text=f"{total:.2f} {currency}", text_color="#10B981", font=(self.app_font, 20, "bold")).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))
            ctk.CTkLabel(summary_frame, text=f"{total_spent:.2f} {currency}", text_color="#F59E0B", font=(self.app_font, 20, "bold")).grid(row=1, column=1, sticky="w", padx=20, pady=(0, 20))
            ctk.CTkLabel(summary_frame, text=f"{total_income:.2f} {currency}", text_color="#3B82F6", font=(self.app_font, 20, "bold")).grid(row=1, column=2, sticky="w", padx=20, pady=(0, 20))
            ctk.CTkLabel(summary_frame, text="0", text_color="#8B5CF6", font=(self.app_font, 20, "bold")).grid(row=1, column=3, sticky="w", padx=20, pady=(0, 20))

            # 2. Kafelek wyróżnienia (Środek)
            highlight_frame = ctk.CTkFrame(stat_scroll, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
            highlight_frame.pack(fill="x", padx=20, pady=(0, 20))
            ctk.CTkLabel(highlight_frame, text="Największa kategoria wydatków", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(highlight_frame, text=max_category, text_color="#10B981", font=(self.app_font, 18, "bold")).pack(anchor="w", padx=20, pady=(0, 15))

            # 3. Dolna siatka podziału na dwie kolumny (Dół)
            bottom_grid = ctk.CTkFrame(stat_scroll, fg_color="transparent")
            bottom_grid.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            bottom_grid.grid_columnconfigure(0, weight=1, uniform="group1")
            bottom_grid.grid_columnconfigure(1, weight=1, uniform="group1")
            bottom_grid.grid_rowconfigure(0, weight=1)

            # Lewa kolumna: Lista transakcji
            list_frame = ctk.CTkFrame(bottom_grid, fg_color="transparent")
            list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            ctk.CTkLabel(list_frame, text="Statystyki i wydatki według tagów", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 14, "bold")).pack(anchor="w", pady=(0, 10))

            for item in stats:
                card = ctk.CTkFrame(list_frame, fg_color=("#F3F4F6", "#252837"), corner_radius=8)
                card.pack(fill="x", pady=4)
                ctk.CTkLabel(card, text=item['tag'], text_color=("#111827", "#F8FAFC"), font=(self.app_font, 14, "bold")).pack(side="left", padx=15, pady=15)
                ctk.CTkLabel(card, text=f"Wydano: {item['spent']:.2f} {currency}  •  Wpłaty: {item['income']:.2f} {currency}", text_color=("#4B5563", "#94A3B8"), font=(self.app_font, 11)).pack(side="right", padx=15)

            if not stats:
                ctk.CTkLabel(list_frame, text="Brak danych", text_color=("#4B5563", "#CBD5E1"), font=(self.app_font, 13)).pack(pady=20)

            # Prawa kolumna: Wykres kołowy (Donut Chart)
            chart_frame = ctk.CTkFrame(bottom_grid, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
            chart_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            
            ctk.CTkLabel(chart_frame, text="Statystyki całkowitych wydatków", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 14, "bold")).pack(pady=(15, 0))

            current_mode = ctk.get_appearance_mode()
            bg_color = '#F3F4F6' if current_mode == 'Light' else '#252837'
            text_color = '#000000' if current_mode == 'Light' else 'white'

            fig = Figure(figsize=(5, 4), facecolor=bg_color)
            ax = fig.add_subplot(111)
            ax.set_facecolor(bg_color)

            spent_stats = [s for s in stats if s['spent'] > 0]
            if spent_stats:
                tags = [s['tag'] for s in spent_stats]
                amounts = [s['spent'] for s in spent_stats]
                ios_colors = ['#34C759', '#FF9500', '#007AFF', '#FF3B30', '#5AC8FA', '#5856D6', '#AF52DE']

                wedges, texts, autotexts = ax.pie(
                    amounts, labels=tags, autopct='%1.0f%%', startangle=140,
                    colors=ios_colors[:len(tags)],
                    textprops=dict(color=text_color, size=9, fontname=self.app_font),
                    wedgeprops=dict(width=0.35, edgecolor=bg_color, linewidth=2)
                )
                for autotext in autotexts:
                    autotext.set_color('#FFFFFF')
                    autotext.set_weight('bold')
                    autotext.set_size(8)
            else:
                ax.text(0.5, 0.5, "Brak danych do wykresu", ha='center', va='center', color=text_color, fontname=self.app_font)
                ax.axis('off')

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.configure(bg=bg_color, highlightthickness=0)
            canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
            canvas.draw()

        elif self.view_var == "Ustawienia":
            settings_scroll = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            settings_scroll.pack(fill="both", expand=True)

            ctk.CTkLabel(settings_scroll, text="Ustawienia Systemowe", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 24, "bold")).pack(anchor="w", padx=20, pady=(20, 10))

            theme_frame = ctk.CTkFrame(settings_scroll, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
            theme_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(theme_frame, text="Opcje regionalne i wygląd", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
            
            def change_appearance_mode(new_mode):
                ctk.set_appearance_mode(new_mode)
                self.trigger_render()
                
            ctk.CTkLabel(theme_frame, text="Motyw aplikacji:", text_color=("#6B7280", "#94A3B8"), font=(self.app_font, 12)).pack(anchor="w", padx=15, pady=(0, 2))
            theme_combo = ctk.CTkComboBox(
                theme_frame, 
                values=["Dark", "Light"], 
                command=change_appearance_mode,
                fg_color=("#FFFFFF", "#1B1D29"), 
                border_color=("#D1D5DB", "#334155"), 
                button_color=("#D1D5DB", "#334155"), 
                text_color=("#111827", "#FFFFFF"),
                font=(self.app_font, 12)
            )
            theme_combo.pack(anchor="w", padx=15, pady=(0, 10))
            theme_combo.set(ctk.get_appearance_mode())

            def change_font(new_font):
                self.db.set_font(new_font)
                self.trigger_render()

            ctk.CTkLabel(theme_frame, text="Czcionka aplikacji:", text_color=("#6B7280", "#94A3B8"), font=(self.app_font, 12)).pack(anchor="w", padx=15, pady=(5, 2))
            font_combo = ctk.CTkComboBox(
                theme_frame,
                values=["Segoe UI", "Arial", "Helvetica", "Verdana", "Trebuchet MS", "Comic Sans MS"],
                command=change_font,
                fg_color=("#FFFFFF", "#1B1D29"), 
                border_color=("#D1D5DB", "#334155"), 
                button_color=("#D1D5DB", "#334155"), 
                text_color=("#111827", "#FFFFFF"),
                font=(self.app_font, 12)
            )
            font_combo.pack(anchor="w", padx=15, pady=(0, 10))
            font_combo.set(self.app_font)

            def change_currency(new_currency):
                self.db.set_currency(new_currency)
                self.trigger_render()

            ctk.CTkLabel(theme_frame, text="Domyślna waluta:", text_color=("#6B7280", "#94A3B8"), font=(self.app_font, 12)).pack(anchor="w", padx=15, pady=(5, 2))
            currency_combo = ctk.CTkComboBox(
                theme_frame,
                values=["zł", "USD", "EUR", "GBP", "CHF"],
                command=change_currency,
                fg_color=("#FFFFFF", "#1B1D29"), 
                border_color=("#D1D5DB", "#334155"), 
                button_color=("#D1D5DB", "#334155"), 
                text_color=("#111827", "#FFFFFF"),
                font=(self.app_font, 12)
            )
            currency_combo.pack(anchor="w", padx=15, pady=(0, 15))
            currency_combo.set(currency)

            db_frame = ctk.CTkFrame(settings_scroll, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
            db_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(db_frame, text="Baza danych", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
            
            import os
            db_path = os.path.abspath(os.path.join("data", "simple_budget.sqlite3"))
            
            ctk.CTkLabel(db_frame, text="Ścieżka zapisu (do kopii zapasowej):", text_color=("#6B7280", "#94A3B8"), font=(self.app_font, 12)).pack(anchor="w", padx=15, pady=(0, 2))
            
            path_entry = ctk.CTkEntry(db_frame, fg_color=("#FFFFFF", "#1B1D29"), border_color=("#D1D5DB", "#334155"), text_color=("#111827", "#F8FAFC"), width=400, font=(self.app_font, 12))
            path_entry.pack(anchor="w", padx=15, pady=(0, 15))
            path_entry.insert(0, db_path)
            path_entry.configure(state="readonly")

            reset_frame = ctk.CTkFrame(settings_scroll, fg_color=("#F3F4F6", "#252837"), corner_radius=10)
            reset_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(reset_frame, text="Resetowanie danych", text_color=("#111827", "#F8FAFC"), font=(self.app_font, 16, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
            ctk.CTkLabel(reset_frame, text="Permanentne usunięcie wszystkich zarejestrowanych kont oraz pełnej historii wpisów.", text_color=("#6B7280", "#94A3B8"), font=(self.app_font, 12)).pack(anchor="w", padx=15, pady=(0, 10))
            
            ctk.CTkButton(
                reset_frame, 
                text="Zresetuj wszystkie dane", 
                fg_color="#EF4444", 
                hover_color="#DC2626", 
                text_color="#FFFFFF",
                font=(self.app_font, 12, "bold"),
                command=self.reset_application_data
            ).pack(anchor="w", padx=15, pady=(0, 15))

    def reset_application_data(self):
        if messagebox.askyesno("Potwierdzenie resetu", "Czy na pewno chcesz zresetować wszystkie dane?\n\nTa operacja całkowicie usunie wszystkie konta oraz historię wpisów. Nie można tego cofnąć!"):
            try:
                with self.db.conn:
                    cur = self.db.conn.cursor()
                    cur.execute("PRAGMA foreign_keys = OFF;")
                    cur.execute("DELETE FROM transactions;")
                    cur.execute("DELETE FROM accounts;")
                    cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('transactions', 'accounts');")
                    cur.execute("PRAGMA foreign_keys = ON;")
                self.trigger_render()
                messagebox.showinfo("Sukces", "Wszystkie dane zostały pomyślnie usunięte.")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się zresetować danych: {str(e)}")

    def add_account(self):
        AccountDialog(self, on_saved=self._save_account)

    def edit_account(self, account):
        AccountDialog(self, on_saved=self._save_account, account=account)

    def show_account_details(self, account):
        AccountDetailsDialog(self, account, self.db, self.db.get_currency())

    def delete_account(self, account):
        if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć konto '{account['name']}'?\n\nUsunięte zostaną też przypisane wpisy!"):
            self.db.delete_account(account['id'])
            self.trigger_render()

    def _save_account(self, account_id, name, balance, color):
        if account_id is None:
            self.db.add_account(name, balance, color)
        else:
            self.db.update_account(account_id, name, balance, color)
        self.trigger_render()

    def open_add_menu(self):
        accounts = self.db.accounts()
        tags = self.db.tags()
        if not accounts:
            messagebox.showwarning("Uwaga", "Musisz najpierw utworzyć konto.")
            return
        AddTransactionDialog(self, accounts, tags, on_saved=self._save_transaction)

    def open_transfer_menu(self):
        accounts = self.db.accounts()
        if len(accounts) < 2:
            messagebox.showwarning("Uwaga", "Do wykonania przelewu wymagane są co najmniej dwa konta.")
            return
        TransferDialog(self, accounts, on_saved=self._save_transfer)

    def repeat_transaction(self, transaction):
        accounts = self.db.accounts()
        tags = self.db.tags()
        AddTransactionDialog(self, accounts, tags, on_saved=self._save_transaction, transaction=transaction)

    def _save_transaction(self, kind, amount, account_id, tag, note, tx_date):
        self.db.add_transaction(kind, amount, account_id, tag, note, tx_date)
        self.trigger_render()

    def _save_transfer(self, from_account_id, to_account_id, amount, note, tx_date):
        self.db.add_transfer(from_account_id, to_account_id, amount, note, tx_date)
        self.trigger_render()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = SimpleBudgetApp()
    try:
        app.mainloop()
    finally:
        app.db.close()