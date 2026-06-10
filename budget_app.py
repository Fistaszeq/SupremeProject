"""
Plik 2:
Moduł głównej aplikacji GUI. Zoptymalizowany pod kątem responsywności i
asynchronicznego ładowania widoków. Wzbogacony o wykres kołowy statystyk.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from budget_db import SimpleBudgetDB
from budget_dialogs import AccountDialog, AddTransactionDialog, AccountDetailsDialog


class SimpleBudgetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget iOS")
        self.geometry("1200x900")
        self.minsize(380, 760)
        self.configure(fg_color="#111217")
        self.db = SimpleBudgetDB()

        top = ctk.CTkFrame(self, fg_color="#1B1D29", corner_radius=10)
        top.pack(fill="x", padx=8, pady=(14, 8))
        ctk.CTkLabel(top, text="BudgetFlow", text_color="#F8FAFC", font=("Segoe UI", 32, "bold")).pack(side="left", padx=20, pady=10)

        self.view_var = "Main"

        ctk.CTkButton(top, text="Statystyki", fg_color="transparent",
                      hover_color="#111217", font=("Segoe UI", 14, "bold"), command=lambda:
                      self.switch_view("Statystyki")).pack(side="right", padx=(4, 8))
        ctk.CTkButton(top, text="Strona główna", fg_color="transparent",
                      hover_color="#111217", font=("Segoe UI", 14, "bold"), command=lambda:
                      self.switch_view("Main")).pack(side="right", padx=(4, 4))

        self.main_container = ctk.CTkFrame(self, fg_color="#1B1D29", corner_radius=10)
        self.main_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.frames = {
            "Main": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Statystyki": ctk.CTkFrame(self.main_container, fg_color="transparent")
        }

        self.loading_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.loading_spinner = ctk.CTkLabel(self.loading_frame, text="Ładowanie danych...", text_color="#8E8E93", font=("Segoe UI", 20, "bold"))
        self.loading_spinner.place(relx=0.5, rely=0.5, anchor="center")
        
        self.fab = ctk.CTkButton(self, text="+", fg_color="#6E5BE8", hover_color="#4b39bf",
                                 font=("Segoe UI", 24, "bold"), width=50, height=50, corner_radius=10,
                                 command=self.open_add_menu)
        self.fab.place(relx=1.0, rely=1.0, x=-36, y=-18, anchor="se")
        
        self.fab.lift()
        
        self.trigger_render()

    def switch_view(self, view_name):
        if self.view_var == view_name:
            return
        self.view_var = view_name
        self.trigger_render()

    def trigger_render(self):
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

        if self.view_var == "Main":
            #Zakladka main
            accounts = self.db.accounts()
            total = sum(a['balance'] for a in accounts)
            color_family = ["#2563EB", "#1E3A8A", "#8B5CF6", "#4C1D95", "#10B981", "#064E3B", "#F59E0B", "#78350F"]

            current_frame.grid_columnconfigure(0, weight=1, uniform="group1")
            current_frame.grid_columnconfigure(1, weight=1, uniform="group1")
            current_frame.grid_rowconfigure(0, weight=1)

            body_left = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            body_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

            ctk.CTkLabel(body_left, text="Łącznie na wszystkich kontach", text_color="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=8, pady=(4, 0))
            ctk.CTkLabel(body_left, text=f"{total:.2f} zł", text_color="#F8FAFC", font=("Segoe UI", 32, "bold")).pack(anchor="w", padx=8, pady=(2, 12))

            if not accounts:
                empty = ctk.CTkFrame(body_left, fg_color="#252837", corner_radius=10)
                empty.pack(fill="x", padx=8, pady=6)
                ctk.CTkLabel(empty, text="Brak kont – dodaj pierwsze konto", text_color="#CBD5E1", font=("Segoe UI", 14)).pack(pady=18)
            else:
                for idx, account in enumerate(accounts):
                    card_color = color_family[idx % len(color_family)]
                    card = ctk.CTkFrame(body_left, fg_color=card_color, corner_radius=12)
                    card.pack(fill="x", padx=8, pady=6)

                    ctk.CTkLabel(card, text=account['name'], text_color="#F8FAFC", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(12, 0))
                    ctk.CTkLabel(card, text=f"{account['balance']:.2f} zł", text_color="#FFFFFF", font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=16, pady=(0, 2))

                    if account.get('last_date'):
                        sign = "+" if account['last_kind'] == "Wpłata" else "-"
                        last_info = f"Ostatnio: {account['last_date']} ({sign}{account['last_amount']:.2f} zł)"
                    else:
                        last_info = "Ostatnio: Brak transakcji"

                    ctk.CTkLabel(card, text=last_info, text_color="#AEAEB2", font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(0, 10))

                    btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                    btn_frame.pack(fill="x", padx=16, pady=(0, 12))
                    
                    ctk.CTkButton(btn_frame, text="Szczegóły", width=75, height=24, fg_color="#0A84FF", hover_color="#0066CC", text_color="#FFFFFF", font=("Segoe UI", 11, "bold"), command=lambda a=account: self.show_account_details(a)).pack(side="left", padx=(0, 8))
                    ctk.CTkButton(btn_frame, text="Edytuj", width=65, height=24, fg_color="#334155", hover_color="#475569", text_color="#F8FAFC", font=("Segoe UI", 11, "bold"), command=lambda a=account: self.edit_account(a)).pack(side="left", padx=(0, 8))
                    ctk.CTkButton(btn_frame, text="Usuń", width=65, height=24, fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF", font=("Segoe UI", 11, "bold"), command=lambda a=account: self.delete_account(a)).pack(side="left")

            ctk.CTkButton(body_left, text="Dodaj konto", fg_color="#6E5BE8", hover_color="#4b39bf", font=("Segoe UI", 14, "bold"), corner_radius=10, command=self.add_account).pack(pady=10)

            body_right = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            body_right.grid(row=0, column=1, sticky="nsew", padx=(6,  0))

            history = ctk.CTkFrame(body_right, fg_color="#111217", corner_radius=10)
            history.pack(fill="both", padx=8, pady=(8,  8), expand=True)
            ctk.CTkLabel(history, text="Historia wpisów", text_color="#F8FAFC", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=14, pady=(10, 6))

            for item in self.db.transactions():
                row = ctk.CTkFrame(history, fg_color="#252837", corner_radius=10)
                row.pack(fill="x", padx=10, pady=6)

                top_row = ctk.CTkFrame(row, fg_color="transparent")
                top_row.pack(fill="x", padx=14, pady=(12, 2))

                title_text = item['note'] if item['note'] else item['tag']
                ctk.CTkLabel(top_row, text=title_text, text_color="#F8FAFC", font=("Segoe UI", 15, "bold")).pack(side="left")

                sign = "+" if item['kind'] == "Wpłata" else "-"
                status_color = "#34C759" if item['kind'] == "Wpłata" else "#FF3B30"
                ctk.CTkLabel(top_row, text=f"{sign}{item['amount']:.2f} zł", text_color=status_color, font=("Segoe UI", 15, "bold")).pack(side="right")

                bottom_row = ctk.CTkFrame(row, fg_color="transparent")
                bottom_row.pack(fill="x", padx=14, pady=(0, 12))

                meta_text = f"{item['created_at']} • {item['account_name']} • {item['tag']}"
                ctk.CTkLabel(bottom_row, text=meta_text, text_color="#94A3B8", font=("Segoe UI", 12)).pack(side="left", pady=(2, 0))
                ctk.CTkButton(bottom_row, text="Ponów", width=60, height=24, fg_color="#3A3A3C", hover_color="#48484A", text_color="#FFFFFF", font=("Segoe UI", 11, "bold"), command=lambda t=item: self.repeat_transaction(t)).pack(side="right")

        elif self.view_var == "Statystyki":
            #Zakladka statystyki
            stat_scroll = ctk.CTkScrollableFrame(current_frame, fg_color="transparent")
            stat_scroll.pack(fill="both", expand=True)

            ctk.CTkLabel(stat_scroll, text="Statystyki Globalne", text_color="#F8FAFC", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=20, pady=(20,  10))

            stat_frame = ctk.CTkFrame(stat_scroll, fg_color="transparent")
            stat_frame.pack(fill="both", expand=True)
            stat_frame.grid_columnconfigure(0, weight=1, uniform="group2")
            stat_frame.grid_columnconfigure(1, weight=1, uniform="group2")
            stat_frame.grid_rowconfigure(0, weight=0)
            stat_frame.grid_rowconfigure(1, weight=1)

            stat_left = ctk.CTkScrollableFrame(stat_frame, fg_color="transparent", label_text="")
            stat_left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 6))

            ctk.CTkLabel(stat_left, text="Statystyki i wydatki według tagów", text_color="#F8FAFC", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=8, pady=(4, 8))

            pie_chart_container = ctk.CTkFrame(stat_frame, fg_color="transparent")
            pie_chart_container.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

            stats = self.db.stats()
            
            if stats:
                # Filtrowanie etykiet i wartości tylko dla wydatków większych od zera
                labels = [item["tag"] for item in stats if item["spent"] > 0]
                sizes = [item["spent"] for item in stats if item["spent"] > 0]

                #Ramka na wykres kołowy
                pie_chart_frame = ctk.CTkFrame(pie_chart_container, fg_color="#252837", corner_radius=10)
                pie_chart_frame.pack(fill="x", padx=8, pady=6)

                bar_chart_container = ctk.CTkFrame(stat_frame, fg_color="transparent")
                bar_chart_container.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(10, 0))


                if sizes:
                    #Tworzenie wykresu kołowego
                    fig, ax = plt.subplots(figsize=(4, 4), facecolor='#252837')
                    ax.set_facecolor('#252837')

                    colors = ['#6E5BE8', '#95E8A8', '#F1C40F']
                    wedges, texts, autotexts = ax.pie(
                        sizes, labels=labels, 
                        autopct='%1.0f%%', startangle=90,
                        colors=colors[:len(sizes)],
                        textprops=dict(color="#F8FAFC"), 
                        wedgeprops={"width": 0.4, "edgecolor": "#252837"}
                    )

                    #Kolor tekstu na wykresie
                    for autotext in autotexts:
                        autotext.set_color("#F8FAFC")
                        autotext.set_weight('bold')

                    ax.axis("equal")
                    ax.set_title("Statystyki całkowitych wydatków", color="#F8FAFC", fontname="Segoe UI", fontsize=14, fontweight="bold", pad=8)

                    #Rysowanie wykresu kołowego
                    canvas_pie_chart = FigureCanvasTkAgg(fig, master=pie_chart_frame)
                    canvas_pie_chart.draw()
                    canvas_pie_chart.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
                    plt.close(fig)
                else:
                    ctk.CTkLabel(pie_chart_frame, text="Brak danych o wydatkach", text_color="#CBD5E1", font=("Segoe UI", 14)).pack(expand=True, pady=20)

                #Wykres slupkowy
                from collections import defaultdict
                from datetime import datetime, timedelta

                raw_daily_expenses = defaultdict(float)
                for tx in self.db.transactions():
                    if tx['kind'] != "Wpłata":
                        date_str = tx['created_at'].split(" ") if " " in tx['created_at'] else tx['created_at']
                        raw_daily_expenses[date_str] += float(tx['amount'])

                #Generwoanie ostatniego tygodnia
                sorted_dates = []
                daily_spent = []
                
                today = datetime.now()
                for i in range(6, -1, -1):
                    day = today - timedelta(days=i)
                    date_str = day.strftime("%Y-%m-%d")
                    sorted_dates.append(date_str)
                    daily_spent.append(raw_daily_expenses.get(date_str, 0.0))

                #Rysowanie wykresu
                bar_chart_frame = ctk.CTkFrame(bar_chart_container, fg_color="#252837", corner_radius=10)
                bar_chart_frame.pack(fill="both", expand=True, padx=8, pady=6)

                fig_bar = Figure(figsize=(5, 3), facecolor='#252837')
                ax_bar = fig_bar.add_subplot(111)
                ax_bar.set_facecolor("#252837")
                
                bars = ax_bar.bar(sorted_dates, daily_spent, color="#6E5BE8", width=0.5)
                ax_bar.set_title("Całkowite wydatki z ostatnich 7 dni", color="white", fontsize=12, fontweight="bold", pad=10)
                ax_bar.tick_params(colors='white', labelsize=10, axis='x', rotation=45)
                ax_bar.tick_params(colors='white', labelsize=10, axis='y')
                
                for spine in ax_bar.spines.values(): 
                    spine.set_visible(False)
                fig_bar.tight_layout()

                canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_chart_frame)
                canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
                canvas_bar.draw()

                for item in stats:
                    card = ctk.CTkFrame(stat_left, fg_color="#252837", corner_radius=10)
                    card.pack(fill="x", padx=8, pady=6)

                    ctk.CTkLabel(card, text=item['tag'], text_color="#F8FAFC", font=("Segoe UI", 14, "bold")).pack(side="left", padx=15, pady=15)
                    
                    info_text = f"Wydano: {item['spent']:.2f} zł  •  Wpłaty: {item['income']:.2f} zł"
                    ctk.CTkLabel(card, text=info_text, text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="right", padx=15)
            else:
                ctk.CTkLabel(stat_left, text="Brak danych – dodaj pierwszy wpis", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(pady=20)

    def add_account(self):
        AccountDialog(self, on_saved=self._save_account)

    def edit_account(self, account):
        AccountDialog(self, on_saved=self._save_account, account=account)

    def show_account_details(self, account):
        AccountDetailsDialog(self, account, self.db)

    def delete_account(self, account):
        if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć konto '{account['name']}'?\nUsunięte zostaną też przypisane wpisy!"):
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

    def repeat_transaction(self, transaction):
        accounts = self.db.accounts()
        tags = self.db.tags()
        AddTransactionDialog(self, accounts, tags, on_saved=self._save_transaction, transaction=transaction)

    def _save_transaction(self, self_param, kind, amount, account_id, tag, note, tx_date):
        self.db.add_transaction(kind, amount, account_id, tag, note, tx_date)
        self.trigger_render()


#Uruchamianie aplikacji
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = SimpleBudgetApp()
    try:
        app.mainloop()
    finally:
        app.db.close()

