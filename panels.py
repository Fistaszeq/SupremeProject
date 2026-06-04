from gui import customtkinter as ctk
from datetime import date
import calendar
from data_manager import (init_data, load_transactions, load_categories, load_goals,
                           save_goals, add_transaction, delete_transaction, load_settings,
                           save_settings, update_setting, add_goal, add_deposit_to_goal)
from logic import (get_monthly_summary, get_today_budget, forecast_month,
                   get_category_breakdown, get_last_n_months_data,
                   get_streak_days, get_biggest_expense_this_month,
                   get_savings_rate, format_currency, animate_counter)
from charts import (DonutChart, SpendingBarChart, MonthTrendChart,
                    DailySpendingChart, GoalProgressRing, SavingsLineChart)

KOLORY = {
    "primary": "#3B82F6", "success": "#10B981", "warning": "#F59E0B",
    "danger": "#EF4444", "purple": "#8B5CF6", "pink": "#EC4899",
    "bg_card": "#252535", "text_dim": "#888899", "text": "#c8c8d4"
}


class PanelManager:
    def __init__(self, frames: dict):
        self.frames = frames
        self.current_panel = None
        self._nav_buttons = {}
        self.font_title = ctk.CTkFont("Segoe UI", 26, "bold")
        self.font_big = ctk.CTkFont("Segoe UI", 22, "bold")
        self.font_mid = ctk.CTkFont("Segoe UI", 14)
        self.font_mid_b = ctk.CTkFont("Segoe UI", 14, "bold")
        self.font_small = ctk.CTkFont("Segoe UI", 11)
        self.font_label = ctk.CTkFont("Segoe UI", 12, "bold")
        self.font_tiny = ctk.CTkFont("Segoe UI", 10)
        self.show_dashboard()

    def register_nav_buttons(self, buttons: dict):
        self._nav_buttons = buttons
        self._highlight("dashboard")

    def _highlight(self, active: str):
        for name, btn in self._nav_buttons.items():
            btn.configure(fg_color=KOLORY["primary"] if name == active else "transparent")

    def _clear(self):
        for frame in self.frames.values():
            for widget in frame.winfo_children():
                widget.destroy()

    # ─── DASHBOARD ─────────────────────────────────
    def show_dashboard(self):
        try:
            self._clear()
            self._highlight("dashboard")
            today = date.today()
            summary = get_monthly_summary(today.year, today.month)
            budget_data = get_today_budget()
            forecast = forecast_month(today.year, today.month)
            transactions = load_transactions()
            cat_data = get_category_breakdown(today.year, today.month)
            streak = get_streak_days()
            savings_rate = get_savings_rate(today.year, today.month)
            biggest = get_biggest_expense_this_month()

            # --- left_top: Budżet na dziś ---
            f = self.frames["left_top"]
            ctk.CTkLabel(f, text="💰 Budżet na dziś", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)

            daily_pct = min(100, budget_data["percent_of_daily"])
            if budget_data["status"] == "ok":
                color = KOLORY["success"]
            elif budget_data["status"] == "warning":
                color = KOLORY["warning"]
            else:
                color = KOLORY["danger"]
            donut = DonutChart(f, percent=daily_pct, label="", color=color, width=175, height=175)
            donut.place(x=0, y=28)

            lbl_spent = ctk.CTkLabel(f, text="", font=self.font_big, text_color=KOLORY["danger"])
            lbl_remaining = ctk.CTkLabel(f, text="", font=self.font_mid_b, text_color=color)
            lbl_limit = ctk.CTkLabel(f, text="", font=self.font_small, text_color=KOLORY["text_dim"])

            ctk.CTkLabel(f, text="Dziś wydano:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=185, y=50)
            lbl_spent.place(x=185, y=70)
            ctk.CTkLabel(f, text="Zostało:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=185, y=100)
            lbl_remaining.place(x=185, y=120)
            ctk.CTkLabel(f, text="Dzienny limit:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=185, y=155)
            lbl_limit.place(x=185, y=175)

            animate_counter(lbl_spent, budget_data["today_spent"], format_currency)
            animate_counter(lbl_remaining, abs(budget_data["remaining_today"]), format_currency)
            lbl_limit.configure(text=format_currency(budget_data["daily_budget"]))

            # --- right_top: Miesiąc w skrócie ---
            f = self.frames["right_top"]
            month_names_pl = ["Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec",
                              "Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]
            ctk.CTkLabel(f, text=f"📅 {month_names_pl[today.month-1]} {today.year}",
                         font=self.font_label, text_color=KOLORY["text_dim"]).place(x=12, y=8)

            # Blok 1: Przychody
            b1 = ctk.CTkFrame(f, width=145, height=75, corner_radius=8, fg_color="#252535")
            b1.place(x=10, y=35)
            ctk.CTkLabel(b1, text="📈 Przychody", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=5, y=5)
            lbl_inc = ctk.CTkLabel(b1, text="", font=self.font_big, text_color=KOLORY["success"])
            lbl_inc.place(relx=0.5, rely=0.65, anchor="center")
            animate_counter(lbl_inc, summary["income"], format_currency)

            # Blok 2: Wydatki
            b2 = ctk.CTkFrame(f, width=145, height=75, corner_radius=8, fg_color="#252535")
            b2.place(x=190, y=35)
            ctk.CTkLabel(b2, text="📉 Wydatki", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=5, y=5)
            lbl_exp = ctk.CTkLabel(b2, text="", font=self.font_big, text_color=KOLORY["danger"])
            lbl_exp.place(relx=0.5, rely=0.65, anchor="center")
            animate_counter(lbl_exp, summary["expense"], format_currency)

            # Blok 3: Bilans
            b3 = ctk.CTkFrame(f, width=145, height=75, corner_radius=8, fg_color="#252535")
            b3.place(x=10, y=125)
            ctk.CTkLabel(b3, text="💹 Bilans", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=5, y=5)
            bal_color = KOLORY["success"] if summary["balance"] >= 0 else KOLORY["danger"]
            lbl_bal = ctk.CTkLabel(b3, text="", font=self.font_big, text_color=bal_color)
            lbl_bal.place(relx=0.5, rely=0.65, anchor="center")
            animate_counter(lbl_bal, summary["balance"], format_currency)

            # Blok 4: Stopa oszczędności
            b4 = ctk.CTkFrame(f, width=145, height=75, corner_radius=8, fg_color="#252535")
            b4.place(x=190, y=125)
            ctk.CTkLabel(b4, text="💾 Stopa oszcz.", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=5, y=5)
            ctk.CTkLabel(b4, text=f"{savings_rate:.1f}%", font=self.font_big, text_color=KOLORY["purple"]).place(relx=0.5, rely=0.65, anchor="center")

            # --- left_bottom: Prognoza ---
            f = self.frames["left_bottom"]
            ctk.CTkLabel(f, text="🔮 Prognoza miesiąca", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)

            month_pct = min(100, budget_data["month_percent"])
            if month_pct < 70:
                m_color = KOLORY["success"]
            elif month_pct < 95:
                m_color = KOLORY["warning"]
            else:
                m_color = KOLORY["danger"]
            donut2 = DonutChart(f, percent=month_pct, label="", color=m_color, width=175, height=175)
            donut2.place(x=0, y=28)

            lbl_month_spent = ctk.CTkLabel(f, text="", font=self.font_big, text_color=KOLORY["danger"])
            lbl_month_spent.place(x=185, y=50)
            ctk.CTkLabel(f, text="Wydano w mies.:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=185, y=38)
            animate_counter(lbl_month_spent, summary["expense"], format_currency)

            ctk.CTkLabel(f, text=f"Prognoza: {format_currency(forecast['forecast_total'])}",
                         font=self.font_mid_b, text_color=KOLORY["warning"] if forecast["will_exceed"] else KOLORY["text"]).place(x=185, y=95)
            if forecast["will_exceed"]:
                ctk.CTkLabel(f, text="⚠️", font=self.font_mid_b, text_color=KOLORY["warning"]).place(x=320, y=95)
            ctk.CTkLabel(f, text=f"Budżet: {format_currency(budget_data['monthly_budget'])}",
                         font=self.font_small, text_color=KOLORY["text_dim"]).place(x=185, y=130)

            # --- right_bottom: Statystyki ---
            f = self.frames["right_bottom"]
            ctk.CTkLabel(f, text="⚡ Ciekawostki", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)

            # Streak
            streak_color = KOLORY["success"] if streak >= 7 else KOLORY["warning"] if streak >= 3 else KOLORY["danger"]
            ctk.CTkLabel(f, text="🔥 Seria:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=38)
            ctk.CTkLabel(f, text=f"{streak} dni", font=self.font_big, text_color=streak_color).place(x=12, y=58)

            # Największy wydatek
            if biggest:
                ctk.CTkLabel(f, text="💸 Największy wydatek:", font=self.font_tiny,
                             text_color=KOLORY["text_dim"]).place(x=12, y=110)
                ctk.CTkLabel(f, text=f"{biggest['category_icon']} {format_currency(biggest['amount'])}",
                             font=self.font_mid_b, text_color=KOLORY["danger"]).place(x=12, y=130)
                desc = biggest.get("description", "")[:25] or "—"
                ctk.CTkLabel(f, text=desc, font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=158)
            else:
                ctk.CTkLabel(f, text="Brak wydatków\nw tym miesiącu ✅", font=self.font_mid,
                             text_color=KOLORY["success"]).place(x=12, y=110)

            ctk.CTkLabel(f, text=f"📊 {summary['transaction_count']} transakcji",
                         font=self.font_small, text_color=KOLORY["text_dim"]).place(x=12, y=188)

            # --- bottom: Wydatki dzienne ---
            f = self.frames["bottom"]
            ctk.CTkLabel(f, text="📊 Wydatki dzienne w tym miesiącu", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=5)
            daily_chart = DailySpendingChart(f, transactions=transactions,
                                             daily_limit=budget_data["daily_budget"], width=735, height=137)
            daily_chart.place(x=0, y=28)

            # --- right: Kategorie ---
            f = self.frames["right"]
            ctk.CTkLabel(f, text="🏷️ Wydatki wg kategorii", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(relx=0.5, y=8, anchor="n")
            if cat_data:
                bar = SpendingBarChart(f, data=cat_data, width=300, height=595)
                bar.place(x=0, y=32)
            else:
                ctk.CTkLabel(f, text="Brak wydatków\nw tym miesiącu", font=self.font_mid,
                             text_color=KOLORY["text_dim"]).place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"[show_dashboard] Error: {e}")

    # ─── TRANSAKCJE ──────────────────────────────
    def show_transactions(self):
        try:
            self._clear()
            self._highlight("transactions")
            today = date.today()
            transactions = sorted(load_transactions(), key=lambda t: t["date"], reverse=True)
            categories = {c["id"]: c for c in load_categories()}
            summary = get_monthly_summary(today.year, today.month)

            # left_top
            f = self.frames["left_top"]
            ctk.CTkLabel(f, text="💳 Transakcje", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            ctk.CTkButton(f, text="+ Dodaj transakcję", width=160, height=34,
                          font=self.font_small, fg_color=KOLORY["success"],
                          command=self._open_add_form).place(x=185, y=8)

            # Filtry
            ctk.CTkLabel(f, text="Miesiąc:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=52)
            self._filter_month = ctk.CTkOptionMenu(f, values=["Bieżący", "Poprzedni", "Wszystkie"],
                                                   width=130, height=28, font=self.font_small,
                                                   command=lambda _: self.show_transactions())
            self._filter_month.place(x=70, y=50)
            self._filter_month.set("Bieżący")

            ctk.CTkLabel(f, text="Typ:", font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=215, y=52)
            self._filter_type = ctk.CTkOptionMenu(f, values=["Wszystkie", "💰 Przychody", "💸 Wydatki"],
                                                  width=130, height=28, font=self.font_small,
                                                  command=lambda _: self.show_transactions())
            self._filter_type.place(x=248, y=50)
            self._filter_type.set("Wszystkie")

            # right_top – podsumowanie
            f = self.frames["right_top"]
            ctk.CTkLabel(f, text="📊 Podsumowanie miesiąca", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)

            # 3 bloki poziome
            for idx, (title, amount, clr) in enumerate([
                ("📈 Przychody", summary["income"], KOLORY["success"]),
                ("📉 Wydatki", summary["expense"], KOLORY["danger"]),
                ("💹 Bilans", summary["balance"], KOLORY["success"] if summary["balance"] >= 0 else KOLORY["danger"])
            ]):
                x_pos = 10 + idx * 118
                card = ctk.CTkFrame(f, width=105, height=90, corner_radius=8, fg_color="#252535")
                card.place(x=x_pos, y=40)
                ctk.CTkLabel(card, text=title, font=self.font_tiny, text_color=KOLORY["text_dim"]).place(relx=0.5, rely=0.3, anchor="center")
                ctk.CTkLabel(card, text=format_currency(amount), font=self.font_mid_b, text_color=clr).place(relx=0.5, rely=0.65, anchor="center")

            # left_bottom – lista transakcji
            f = self.frames["left_bottom"]
            ctk.CTkLabel(f, text="Historia", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=4)

            # Filtracja
            filter_val = self._filter_month.get() if hasattr(self, "_filter_month") else "Bieżący"
            type_val = self._filter_type.get() if hasattr(self, "_filter_type") else "Wszystkie"
            filtered = transactions
            if filter_val == "Bieżący":
                prefix = f"{today.year}-{today.month:02d}"
                filtered = [t for t in filtered if t["date"].startswith(prefix)]
            elif filter_val == "Poprzedni":
                pm = today.month - 1 if today.month > 1 else 12
                py = today.year if today.month > 1 else today.year - 1
                prefix = f"{py}-{pm:02d}"
                filtered = [t for t in filtered if t["date"].startswith(prefix)]
            if type_val == "💰 Przychody":
                filtered = [t for t in filtered if t["type"] == "income"]
            elif type_val == "💸 Wydatki":
                filtered = [t for t in filtered if t["type"] == "expense"]

            scroll = ctk.CTkScrollableFrame(f, width=338, height=180, fg_color="transparent")
            scroll.place(x=0, y=25)

            for idx, t in enumerate(filtered[:100]):
                cat = categories.get(t.get("category_id", 0), {"icon": "?", "name": "Inne", "color": "#6B7280"})
                color = KOLORY["success"] if t["type"] == "income" else KOLORY["danger"]
                sign = "+" if t["type"] == "income" else "-"

                row = ctk.CTkFrame(scroll, height=36, corner_radius=6,
                                   fg_color="#252535" if idx % 2 == 0 else "transparent")
                row.pack(fill="x", pady=1, padx=2)

                ctk.CTkFrame(row, width=4, height=36, fg_color=cat["color"], corner_radius=2).place(x=0, y=0)
                ctk.CTkLabel(row, text=t["date"][5:], width=42, font=self.font_tiny,
                             text_color=KOLORY["text_dim"]).place(x=8, y=10)
                ctk.CTkLabel(row, text=f"{cat['icon']} {cat['name']}", width=110,
                             font=self.font_tiny).place(x=52, y=10)
                desc = (t.get("description", "") or "—")[:22]
                ctk.CTkLabel(row, text=desc, font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=165, y=10)
                ctk.CTkLabel(row, text=f"{sign}{t['amount']:.2f} zł", font=self.font_small,
                             text_color=color, width=95).place(x=230, y=10)
                ctk.CTkButton(row, text="✕", width=24, height=24, corner_radius=12,
                              fg_color="transparent", hover_color=KOLORY["danger"] + "33",
                              font=self.font_tiny, text_color=KOLORY["text_dim"],
                              command=lambda tid=t["id"]: self._delete_and_refresh(tid)).place(x=328, y=6)

            # right_bottom – wykres kołowy kategorii
            f = self.frames["right_bottom"]
            ctk.CTkLabel(f, text="Kategorie (ten miesiąc)", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            cat_data = get_category_breakdown(today.year, today.month)
            if cat_data:
                bar2 = SpendingBarChart(f, data=cat_data, width=360, height=185)
                bar2.place(x=0, y=30)
            else:
                ctk.CTkLabel(f, text="Brak wydatków", font=self.font_mid,
                             text_color=KOLORY["text_dim"]).place(relx=0.5, rely=0.5, anchor="center")

            # bottom – wykres dzienny
            f = self.frames["bottom"]
            all_t = load_transactions()
            budget_data = get_today_budget()
            ctk.CTkLabel(f, text="📊 Dzienne wydatki", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=5)
            dc = DailySpendingChart(f, transactions=all_t, daily_limit=budget_data["daily_budget"], width=735, height=137)
            dc.place(x=0, y=28)

            # right – ostatnie transakcje (mini)
            f = self.frames["right"]
            ctk.CTkLabel(f, text="🕐 Ostatnio", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(relx=0.5, y=8, anchor="n")
            scroll2 = ctk.CTkScrollableFrame(f, width=285, height=600, fg_color="transparent")
            scroll2.place(x=5, y=32)
            for t in transactions[:20]:
                cat = categories.get(t.get("category_id", 0), {"icon": "?", "color": "#6B7280"})
                color = KOLORY["success"] if t["type"] == "income" else KOLORY["danger"]
                sign = "+" if t["type"] == "income" else "-"
                mini = ctk.CTkFrame(scroll2, height=30, corner_radius=4, fg_color="#252535")
                mini.pack(fill="x", pady=1, padx=2)
                ctk.CTkLabel(mini, text=cat["icon"], font=self.font_small, width=20).place(x=4, y=5)
                ctk.CTkLabel(mini, text=t["date"][5:], font=self.font_tiny,
                             text_color=KOLORY["text_dim"], width=38).place(x=26, y=7)
                ctk.CTkLabel(mini, text=f"{sign}{t['amount']:.0f}zł", font=self.font_small,
                             text_color=color, width=90).place(x=170, y=5)
        except Exception as e:
            print(f"[show_transactions] Error: {e}")

    def _delete_and_refresh(self, tid):
        try:
            delete_transaction(tid)
            self.show_transactions()
        except Exception as e:
            print(f"[_delete_and_refresh] Error: {e}")

    def _open_add_form(self):
        try:
            win = ctk.CTkToplevel()
            win.title("Nowa transakcja")
            win.geometry("380x460")
            win.grab_set()
            win.resizable(False, False)
            win.configure(fg_color="#1e1e2e")

            ctk.CTkLabel(win, text="Dodaj transakcję", font=ctk.CTkFont("Segoe UI", 16, "bold")).place(relx=0.5, y=20, anchor="n")

            type_var = ctk.StringVar(value="💸 Wydatek")
            type_seg = ctk.CTkSegmentedButton(win, values=["💸 Wydatek", "💰 Przychód"],
                                              variable=type_var, width=340, height=36)
            type_seg.place(relx=0.5, y=60, anchor="n")

            ctk.CTkLabel(win, text="Kwota (zł):", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=115)
            amount_entry = ctk.CTkEntry(win, width=340, height=36, placeholder_text="0.00",
                                        font=ctk.CTkFont("Segoe UI", 13))
            amount_entry.place(x=20, y=138)

            ctk.CTkLabel(win, text="Kategoria:", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=188)
            cats = load_categories()
            cat_names = [f"{c['icon']} {c['name']}" for c in cats]
            cat_ids = [c["id"] for c in cats]
            cat_menu = ctk.CTkOptionMenu(win, values=cat_names, width=340, height=36,
                                         font=ctk.CTkFont("Segoe UI", 12))
            cat_menu.place(x=20, y=210)

            ctk.CTkLabel(win, text="Data:", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=260)
            date_entry = ctk.CTkEntry(win, width=340, height=36, placeholder_text="RRRR-MM-DD",
                                      font=ctk.CTkFont("Segoe UI", 12))
            date_entry.insert(0, str(date.today()))
            date_entry.place(x=20, y=282)

            ctk.CTkLabel(win, text="Opis (opcjonalnie):", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=332)
            desc_entry = ctk.CTkEntry(win, width=340, height=36, placeholder_text="np. zakupy w Biedronce",
                                      font=ctk.CTkFont("Segoe UI", 12))
            desc_entry.place(x=20, y=354)

            error_lbl = ctk.CTkLabel(win, text="", text_color=KOLORY["danger"],
                                     font=ctk.CTkFont("Segoe UI", 10))
            error_lbl.place(x=20, y=398)

            def save():
                try:
                    amount = float(amount_entry.get().replace(",", "."))
                    if amount <= 0:
                        raise ValueError("Kwota musi być > 0")
                    type_ = "income" if "Przychód" in type_var.get() else "expense"
                    sel_idx = cat_names.index(cat_menu.get())
                    cat_id = cat_ids[sel_idx]
                    date_str = date_entry.get().strip()
                    desc = desc_entry.get().strip()
                    add_transaction(amount, type_, cat_id, desc, date_str)
                    win.destroy()
                    self.show_transactions()
                except ValueError as e:
                    error_lbl.configure(text=str(e))

            ctk.CTkButton(win, text="💾 Zapisz transakcję", width=340, height=40,
                          fg_color=KOLORY["success"], font=ctk.CTkFont("Segoe UI", 13, "bold"),
                          command=save).place(x=20, y=410)
        except Exception as e:
            print(f"[_open_add_form] Error: {e}")

    # ─── KATEGORIE ────────────────────────────────
    def show_categories(self):
        try:
            self._clear()
            self._highlight("categories")
            today = date.today()
            categories = load_categories()
            cat_breakdown = get_category_breakdown(today.year, today.month)
            breakdown_map = {c["category_id"]: c for c in cat_breakdown}

            # left_top – top 3 paski
            f = self.frames["left_top"]
            ctk.CTkLabel(f, text="🏷️ Kategorie wydatków", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            top3 = cat_breakdown[:3]
            for i, cat in enumerate(top3):
                y_pos = 38 + i * 55
                ctk.CTkLabel(f, text=f"{cat['icon']} {cat['name']}", font=self.font_small).place(x=12, y=y_pos)
                ctk.CTkLabel(f, text=f"{cat['percent']:.0f}%", font=self.font_tiny,
                             text_color=KOLORY["text_dim"]).place(x=290, y=y_pos)
                pb = ctk.CTkProgressBar(f, width=335, height=10, corner_radius=5, progress_color=cat["color"])
                pb.place(x=12, y=y_pos + 20)
                pb.set(cat["percent"] / 100)

            # right_top – największa kategoria
            f = self.frames["right_top"]
            ctk.CTkLabel(f, text="📊 Łączne wydatki w kategorii (ten mies.)", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            if cat_breakdown:
                top_cat = cat_breakdown[0]
                ctk.CTkLabel(f, text=top_cat["icon"], font=ctk.CTkFont("Segoe UI", 40)).place(x=20, y=35)
                ctk.CTkLabel(f, text=top_cat["name"], font=self.font_mid_b).place(x=80, y=45)
                ctk.CTkLabel(f, text=format_currency(top_cat["total"]), font=self.font_big,
                             text_color=top_cat["color"]).place(x=80, y=75)
                ctk.CTkLabel(f, text=f"Stanowi {top_cat['percent']:.0f}% wszystkich wydatków",
                             font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=80, y=120)

            # left_bottom – lista wszystkich kategorii
            f = self.frames["left_bottom"]
            ctk.CTkLabel(f, text="Wszystkie kategorie", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=4)
            scroll = ctk.CTkScrollableFrame(f, width=338, height=178, fg_color="transparent")
            scroll.place(x=0, y=26)
            for cat in categories:
                breakdown = breakdown_map.get(cat["id"])
                row = ctk.CTkFrame(scroll, height=42, corner_radius=8, fg_color="#252535")
                row.pack(fill="x", pady=2, padx=2)
                ctk.CTkFrame(row, width=5, height=42, fg_color=cat["color"], corner_radius=2).place(x=0, y=0)
                ctk.CTkLabel(row, text=f"{cat['icon']} {cat['name']}", font=self.font_small, width=150).place(x=10, y=12)
                type_txt = "wydatek" if cat["type"] == "expense" else "przychód" if cat["type"] == "income" else "oba"
                ctk.CTkLabel(row, text=type_txt, font=self.font_tiny, text_color=KOLORY["text_dim"], width=60).place(x=165, y=12)
                if breakdown:
                    ctk.CTkLabel(row, text=format_currency(breakdown["total"]), font=self.font_small,
                                 text_color=cat["color"], width=100).place(x=230, y=12)
                else:
                    ctk.CTkLabel(row, text="0,00 zł", font=self.font_small,
                                 text_color=KOLORY["text_dim"], width=100).place(x=230, y=12)

            # right_bottom – porównanie z poprzednim miesiącem
            f = self.frames["right_bottom"]
            ctk.CTkLabel(f, text="📈 Trend top kategorii", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            pm = today.month - 1 if today.month > 1 else 12
            py = today.year if today.month > 1 else today.year - 1
            prev_breakdown = {c["category_id"]: c for c in get_category_breakdown(py, pm)}
            for i, cat in enumerate(categories[:5]):
                cid = cat["id"]
                curr = breakdown_map.get(cid, {}).get("total", 0)
                prev = prev_breakdown.get(cid, {}).get("total", 0)
                diff = curr - prev
                arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
                a_color = KOLORY["danger"] if diff > 0 else KOLORY["success"] if diff < 0 else KOLORY["text_dim"]
                y_pos = 35 + i * 36
                ctk.CTkLabel(f, text=f"{cat['icon']} {cat['name']}", font=self.font_small, width=130).place(x=8, y=y_pos)
                ctk.CTkLabel(f, text=format_currency(curr), font=self.font_small,
                             text_color=cat["color"], width=100).place(x=145, y=y_pos)
                ctk.CTkLabel(f, text=f"{arrow} {abs(diff):.0f}zł", font=self.font_tiny,
                             text_color=a_color, width=100).place(x=250, y=y_pos + 2)

            # bottom – wykres słupkowy kategorii
            f = self.frames["bottom"]
            ctk.CTkLabel(f, text="📊 Wydatki według kategorii", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=5)
            if cat_breakdown:
                big_bar = SpendingBarChart(f, data=cat_breakdown, width=735, height=137)
                big_bar.place(x=0, y=28)

            # right – Top wydatek (karty z paskiem)
            f = self.frames["right"]
            ctk.CTkLabel(f, text="🎯 Top wydatek", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(relx=0.5, y=8, anchor="n")
            for i, item in enumerate(cat_breakdown[:8]):
                y_p = 35 + i * 68
                mini_f = ctk.CTkFrame(f, width=280, height=58, corner_radius=8, fg_color="#252535")
                mini_f.place(x=10, y=y_p)
                ctk.CTkLabel(mini_f, text=item["icon"], font=ctk.CTkFont("Segoe UI", 22)).place(x=8, y=10)
                ctk.CTkLabel(mini_f, text=item["name"], font=self.font_small).place(x=44, y=6)
                ctk.CTkLabel(mini_f, text=format_currency(item["total"]), font=self.font_mid_b,
                             text_color=item["color"]).place(x=44, y=28)
                pb = ctk.CTkProgressBar(mini_f, width=130, height=6, corner_radius=3,
                                        progress_color=item["color"])
                pb.place(x=140, y=30)
                pb.set(item["percent"] / 100)
        except Exception as e:
            print(f"[show_categories] Error: {e}")

    # ─── CELE ─────────────────────────────────────
    def show_goals(self):
        try:
            self._clear()
            self._highlight("goals")
            goals = load_goals()
            today = date.today()
            summary = get_monthly_summary(today.year, today.month)

            # left_top – podsumowanie
            f = self.frames["left_top"]
            ctk.CTkLabel(f, text="🎯 Cele oszczędnościowe", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            ctk.CTkButton(f, text="+ Nowy cel", width=130, height=32,
                          fg_color=KOLORY["primary"], font=self.font_small,
                          command=self._open_add_goal_form).place(x=218, y=8)

            total_target = sum(g["target_amount"] for g in goals)
            total_saved = sum(g.get("current_amount", 0) for g in goals)
            completed = sum(1 for g in goals if g.get("current_amount", 0) >= g["target_amount"])

            ctk.CTkLabel(f, text="Łącznie zaoszczędzono:", font=self.font_tiny,
                         text_color=KOLORY["text_dim"]).place(x=12, y=52)
            ctk.CTkLabel(f, text=format_currency(total_saved), font=self.font_big,
                         text_color=KOLORY["success"]).place(x=12, y=72)
            ctk.CTkLabel(f, text=f"z {format_currency(total_target)} celu łącznego • {completed} ukończone",
                         font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=112)

            if total_target > 0:
                pb_global = ctk.CTkProgressBar(f, width=336, height=14, corner_radius=7,
                                               progress_color=KOLORY["purple"])
                pb_global.place(x=12, y=138)
                pb_global.set(min(1.0, total_saved / total_target))
                ctk.CTkLabel(f, text=f"{total_saved / total_target * 100:.1f}% łącznego celu",
                             font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=160)

            # right_top – rekomendacje
            f = self.frames["right_top"]
            ctk.CTkLabel(f, text="💡 Ile możesz odkładać?", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            balance = summary["balance"]
            income = summary["income"]
            savings_rate = (balance / income * 100) if income > 0 else 0

            ctk.CTkLabel(f, text="Wolne środki w tym miesiącu:", font=self.font_tiny,
                         text_color=KOLORY["text_dim"]).place(x=12, y=38)
            bal_color = KOLORY["success"] if balance >= 0 else KOLORY["danger"]
            ctk.CTkLabel(f, text=format_currency(balance), font=self.font_big, text_color=bal_color).place(x=12, y=58)

            ctk.CTkLabel(f, text="Stopa oszczędności:", font=self.font_tiny,
                         text_color=KOLORY["text_dim"]).place(x=12, y=105)
            sr_color = KOLORY["success"] if savings_rate >= 20 else KOLORY["warning"] if savings_rate >= 10 else KOLORY["danger"]
            ctk.CTkLabel(f, text=f"{savings_rate:.1f}%", font=self.font_big, text_color=sr_color).place(x=12, y=125)

            if savings_rate >= 20:
                advice = "💪 Świetnie! Odkładasz ponad 20% dochodu."
            elif savings_rate >= 10:
                advice = "👍 Dobrze. Spróbuj dobić do 20%."
            elif savings_rate > 0:
                advice = "⚠️ Mało. Zalecane min. 10% dochodu."
            else:
                advice = "🚨 Wydajesz więcej niż zarabiasz!"
            ctk.CTkLabel(f, text=advice, font=self.font_small, text_color=KOLORY["text_dim"],
                         wraplength=330).place(x=12, y=178)

            # Karty celów
            if not goals:
                empty_label = ctk.CTkLabel(
                    self.frames["left_bottom"],
                    text="Nie masz jeszcze żadnych celów.\nDodaj pierwszy cel!",
                    font=self.font_mid, text_color=KOLORY["text_dim"], justify="center"
                )
                empty_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                for i, goal in enumerate(goals[:4]):
                    frame_key = "left_bottom" if i < 2 else "right_bottom"
                    f = self.frames[frame_key]
                    y_offset = (i % 2) * 110
                    card = ctk.CTkFrame(f, width=350, height=100, corner_radius=10, fg_color="#252535")
                    card.place(x=5, y=y_offset + 5)

                    ctk.CTkFrame(card, width=350, height=4, corner_radius=0, fg_color=goal["color"]).place(x=0, y=0)
                    ctk.CTkLabel(card, text=goal["name"], font=self.font_mid_b).place(x=10, y=8)
                    percent = min(100, goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    ctk.CTkLabel(card, text=f"{percent:.0f}%", font=self.font_mid_b,
                                 text_color=goal["color"]).place(x=300, y=8)

                    pb_goal = ctk.CTkProgressBar(card, width=330, height=10, corner_radius=5,
                                                 progress_color=goal["color"])
                    pb_goal.place(x=10, y=38)
                    pb_goal.set(percent / 100)

                    ctk.CTkLabel(card, text=f"{format_currency(goal['current_amount'])} / {format_currency(goal['target_amount'])}",
                                 font=self.font_small, text_color=KOLORY["text_dim"]).place(x=10, y=56)

                    remaining = goal["target_amount"] - goal["current_amount"]
                    if balance > 0 and remaining > 0:
                        months_to_goal = int(remaining / balance) + 1
                        ctk.CTkLabel(card, text=f"~{months_to_goal} mies. przy obecnym tempie",
                                     font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=10, y=74)
                    elif percent >= 100:
                        ctk.CTkLabel(card, text="🎉 CEL OSIĄGNIĘTY!", font=self.font_small,
                                     text_color=KOLORY["success"]).place(x=10, y=74)

                    ctk.CTkButton(card, text="+ Wpłata", width=80, height=24,
                                  fg_color=goal["color"], font=self.font_tiny, corner_radius=12,
                                  command=lambda gid=goal["id"], gname=goal["name"]: self._deposit_to_goal(gid, gname)
                                  ).place(x=260, y=70)

            # bottom – symulacja oszczędzania
            f = self.frames["bottom"]
            ctk.CTkLabel(f, text="📈 Symulacja oszczędzania", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=5)
            if goals and balance > 0:
                g = goals[0]
                sim_chart = SavingsLineChart(f, current=g.get("current_amount", 0),
                                             target=g["target_amount"],
                                             monthly_saving=max(balance, 1),
                                             color=g["color"], width=735, height=137)
                sim_chart.place(x=0, y=28)
            else:
                ctk.CTkLabel(f, text="Dodaj cel i zadbaj o pozytywny bilans miesięczny, aby zobaczyć symulację.",
                             font=self.font_mid, text_color=KOLORY["text_dim"]).place(relx=0.5, rely=0.5, anchor="center")

            # right – pierścienie postępu
            f = self.frames["right"]
            ctk.CTkLabel(f, text="📊 Postęp celów", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(relx=0.5, y=8, anchor="n")
            for i, goal in enumerate(goals[:5]):
                ring = GoalProgressRing(f, goal=goal, width=290, height=110)
                ring.place(x=5, y=35 + i * 120)
        except Exception as e:
            print(f"[show_goals] Error: {e}")

    def _open_add_goal_form(self):
        try:
            win = ctk.CTkToplevel()
            win.title("Nowy cel")
            win.geometry("360x320")
            win.grab_set()
            win.resizable(False, False)
            win.configure(fg_color="#1e1e2e")
            ctk.CTkLabel(win, text="Nowy cel oszczędnościowy", font=ctk.CTkFont("Segoe UI", 15, "bold")).place(relx=0.5, y=20, anchor="n")
            ctk.CTkLabel(win, text="Nazwa celu:", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=60)
            name_e = ctk.CTkEntry(win, width=320, height=36, placeholder_text="np. Wakacje na Majorce")
            name_e.place(x=20, y=82)
            ctk.CTkLabel(win, text="Kwota docelowa (zł):", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=132)
            amount_e = ctk.CTkEntry(win, width=320, height=36, placeholder_text="np. 5000")
            amount_e.place(x=20, y=154)
            ctk.CTkLabel(win, text="Kolor (hex):", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=204)
            colors_available = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4"]
            color_var = ctk.StringVar(value="#3B82F6")
            color_menu = ctk.CTkOptionMenu(win, values=colors_available, variable=color_var, width=320, height=36)
            color_menu.place(x=20, y=226)
            err = ctk.CTkLabel(win, text="", text_color=KOLORY["danger"], font=ctk.CTkFont("Segoe UI", 10))
            err.place(x=20, y=272)

            def save_goal():
                try:
                    n = name_e.get().strip()
                    if not n:
                        raise ValueError("Wpisz nazwę celu")
                    a = float(amount_e.get().replace(",", "."))
                    if a <= 0:
                        raise ValueError("Kwota musi być > 0")
                    add_goal(n, a, color_var.get())
                    win.destroy()
                    self.show_goals()
                except ValueError as e:
                    err.configure(text=str(e))

            ctk.CTkButton(win, text="💾 Zapisz cel", width=320, height=40,
                          fg_color=KOLORY["success"], font=ctk.CTkFont("Segoe UI", 13, "bold"),
                          command=save_goal).place(x=20, y=268)
        except Exception as e:
            print(f"[_open_add_goal_form] Error: {e}")

    def _deposit_to_goal(self, goal_id, goal_name):
        try:
            win = ctk.CTkToplevel()
            win.title("Wpłata")
            win.geometry("320x220")
            win.grab_set()
            win.resizable(False, False)
            win.configure(fg_color="#1e1e2e")
            ctk.CTkLabel(win, text=f"Wpłata do: {goal_name}", font=ctk.CTkFont("Segoe UI", 13, "bold")).place(relx=0.5, y=20, anchor="n")
            ctk.CTkLabel(win, text="Kwota wpłaty (zł):", font=ctk.CTkFont("Segoe UI", 11)).place(x=20, y=65)
            amount_e = ctk.CTkEntry(win, width=280, height=36, placeholder_text="0.00")
            amount_e.place(x=20, y=88)
            err = ctk.CTkLabel(win, text="", text_color=KOLORY["danger"], font=ctk.CTkFont("Segoe UI", 10))
            err.place(x=20, y=134)

            def confirm():
                try:
                    a = float(amount_e.get().replace(",", "."))
                    if a <= 0:
                        raise ValueError("Kwota musi być > 0")
                    add_deposit_to_goal(goal_id, a)
                    win.destroy()
                    self.show_goals()
                except ValueError as e:
                    err.configure(text=str(e))

            ctk.CTkButton(win, text="✅ Potwierdź wpłatę", width=280, height=40,
                          fg_color=KOLORY["success"], font=ctk.CTkFont("Segoe UI", 12, "bold"),
                          command=confirm).place(x=20, y=158)
        except Exception as e:
            print(f"[_deposit_to_goal] Error: {e}")

    # ─── RAPORTY ─────────────────────────────────
    def show_reports(self):
        try:
            self._clear()
            self._highlight("reports")
            today = date.today()
            months_data = get_last_n_months_data(6)
            today_summary = get_monthly_summary(today.year, today.month)
            forecast = forecast_month(today.year, today.month)

            # left_top – analiza 6 miesięcy
            f = self.frames["left_top"]
            ctk.CTkLabel(f, text="🏆 Analiza 6 miesięcy", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)

            best_month = max(months_data, key=lambda m: m["balance"]) if months_data else None
            worst_month = min(months_data, key=lambda m: m["balance"]) if months_data else None

            if best_month:
                ctk.CTkLabel(f, text="Najlepszy miesiąc:", font=self.font_tiny,
                             text_color=KOLORY["text_dim"]).place(x=12, y=38)
                ctk.CTkLabel(f, text=f"🥇 {best_month['label']}", font=self.font_mid_b,
                             text_color=KOLORY["success"]).place(x=12, y=58)
                ctk.CTkLabel(f, text=format_currency(best_month["balance"]), font=self.font_big,
                             text_color=KOLORY["success"]).place(x=12, y=82)

            if worst_month:
                ctk.CTkLabel(f, text="Najtrudniejszy miesiąc:", font=self.font_tiny,
                             text_color=KOLORY["text_dim"]).place(x=185, y=38)
                ctk.CTkLabel(f, text=f"⚠️ {worst_month['label']}", font=self.font_mid_b,
                             text_color=KOLORY["warning"]).place(x=185, y=58)
                ctk.CTkLabel(f, text=format_currency(worst_month["balance"]), font=self.font_mid,
                             text_color=KOLORY["warning"]).place(x=185, y=82)

            avg_expense = sum(m["expense"] for m in months_data) / len(months_data) if months_data else 0
            avg_income = sum(m["income"] for m in months_data) / len(months_data) if months_data else 0
            ctk.CTkLabel(f, text=f"Śr. wydatki: {format_currency(avg_expense)}", font=self.font_tiny,
                         text_color=KOLORY["text_dim"]).place(x=12, y=140)
            ctk.CTkLabel(f, text=f"Śr. przychody: {format_currency(avg_income)}", font=self.font_tiny,
                         text_color=KOLORY["text_dim"]).place(x=12, y=162)
            ctk.CTkLabel(f, text=f"Śr. bilans: {format_currency(avg_income - avg_expense)}", font=self.font_small,
                         text_color=KOLORY["success"] if avg_income > avg_expense else KOLORY["danger"]).place(x=12, y=184)

            # right_top – prognoza i alerty
            f = self.frames["right_top"]
            ctk.CTkLabel(f, text="🔮 Prognoza i alerty", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            ctk.CTkLabel(f, text="Prognoza do końca miesiąca:", font=self.font_tiny,
                         text_color=KOLORY["text_dim"]).place(x=12, y=38)
            fc_color = KOLORY["danger"] if forecast["will_exceed"] else KOLORY["success"]
            ctk.CTkLabel(f, text=format_currency(forecast["forecast_total"]), font=self.font_big,
                         text_color=fc_color).place(x=12, y=58)

            if forecast["will_exceed"]:
                ctk.CTkLabel(f, text=f"⚠️ Przekroczysz budżet o {format_currency(forecast['overshoot_by'])}!",
                             font=self.font_small, text_color=KOLORY["warning"], wraplength=330).place(x=12, y=108)
            else:
                ctk.CTkLabel(f, text="✅ Zmieścisz się w budżecie", font=self.font_small,
                             text_color=KOLORY["success"]).place(x=12, y=108)

            ctk.CTkLabel(f, text=f"Śr. dzienny: {format_currency(forecast['daily_average'])}",
                         font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=145)
            ctk.CTkLabel(f, text=f"Pozostało dni: {forecast['days_left']}",
                         font=self.font_tiny, text_color=KOLORY["text_dim"]).place(x=12, y=168)

            # bottom – wykres trendu
            f = self.frames["bottom"]
            ctk.CTkLabel(f, text="📊 Trend finansowy – ostatnie 6 miesięcy", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=5)
            trend_chart = MonthTrendChart(f, months_data=months_data, width=735, height=137)
            trend_chart.place(x=0, y=28)

            # left_bottom – tabela podsumowania
            f = self.frames["left_bottom"]
            ctk.CTkLabel(f, text="Zestawienie miesięczne", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=4)

            header = ctk.CTkFrame(f, width=358, height=22, fg_color="#252535")
            header.place(x=0, y=26)
            for txt, x_pos in [("Miesiąc", 8), ("Przychody", 80), ("Wydatki", 175), ("Bilans", 270)]:
                ctk.CTkLabel(header, text=txt, font=self.font_tiny, text_color=KOLORY["text_dim"], width=80).place(x=x_pos, y=2)

            scroll = ctk.CTkScrollableFrame(f, width=350, height=145, fg_color="transparent")
            scroll.place(x=0, y=50)
            for i, m in enumerate(reversed(months_data)):
                row = ctk.CTkFrame(scroll, height=22, fg_color="#252535" if i % 2 == 0 else "transparent")
                row.pack(fill="x", pady=1)
                bal_col = KOLORY["success"] if m["balance"] >= 0 else KOLORY["danger"]
                ctk.CTkLabel(row, text=m["label"], font=self.font_tiny, width=70).place(x=0, y=2)
                ctk.CTkLabel(row, text=f"{m['income']:.0f}zł", font=self.font_tiny, text_color=KOLORY["success"], width=90).place(x=72, y=2)
                ctk.CTkLabel(row, text=f"{m['expense']:.0f}zł", font=self.font_tiny, text_color=KOLORY["danger"], width=90).place(x=165, y=2)
                ctk.CTkLabel(row, text=f"{m['balance']:.0f}zł", font=self.font_tiny, text_color=bal_col, width=90).place(x=258, y=2)

            # right_bottom – największe kategorie (6 mies.)
            f = self.frames["right_bottom"]
            ctk.CTkLabel(f, text="🔍 Największe kategorie (6 mies.)", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            all_breakdowns = {}
            for m in months_data:
                bd = get_category_breakdown(m["year"], m["month"])
                for item in bd:
                    cid = item["category_id"]
                    if cid not in all_breakdowns:
                        all_breakdowns[cid] = {"name": item["name"], "icon": item["icon"], "color": item["color"], "total": 0}
                    all_breakdowns[cid]["total"] += item["total"]
            sorted_cats = sorted(all_breakdowns.values(), key=lambda x: x["total"], reverse=True)[:6]
            for i, cat in enumerate(sorted_cats):
                y_p = 35 + i * 30
                ctk.CTkLabel(f, text=f"{cat['icon']} {cat['name']}", font=self.font_small, width=140).place(x=8, y=y_p)
                ctk.CTkLabel(f, text=format_currency(cat["total"]), font=self.font_small,
                             text_color=cat["color"], width=120).place(x=155, y=y_p)

            # right – Donut wykorzystania budżetu
            f = self.frames["right"]
            ctk.CTkLabel(f, text="📌 Miesięczny budżet", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(relx=0.5, y=8, anchor="n")
            budget_data = get_today_budget()
            donut = DonutChart(f, percent=min(100, budget_data["month_percent"]),
                               label="budżetu",
                               color=KOLORY["success"] if budget_data["month_percent"] < 80 else KOLORY["warning"] if budget_data["month_percent"] < 100 else KOLORY["danger"],
                               width=250, height=250)
            donut.place(x=25, y=35)
            ctk.CTkLabel(f, text=f"Wydano: {format_currency(budget_data['month_expense'])}", font=self.font_small).place(x=20, y=295)
            ctk.CTkLabel(f, text=f"Budżet: {format_currency(budget_data['monthly_budget'])}",
                         font=self.font_small, text_color=KOLORY["text_dim"]).place(x=20, y=318)
        except Exception as e:
            print(f"[show_reports] Error: {e}")

    # ─── USTAWIENIA ──────────────────────────────
    def show_settings(self):
        try:
            self._clear()
            self._highlight("settings")
            settings = load_settings()

            # left_top
            f = self.frames["left_top"]
            ctk.CTkLabel(f, text="⚙️ Ustawienia", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)

            ctk.CTkLabel(f, text="Miesięczny budżet (zł):", font=self.font_small).place(x=12, y=45)
            budget_entry = ctk.CTkEntry(f, width=200, height=36, font=self.font_mid,
                                        placeholder_text="np. 3000")
            budget_entry.insert(0, str(settings.get("monthly_budget", 3000.0)))
            budget_entry.place(x=12, y=70)

            ctk.CTkLabel(f, text="Motyw:", font=self.font_small).place(x=12, y=120)
            theme_switch = ctk.CTkSwitch(f, text="Ciemny motyw", font=self.font_small,
                                         onvalue="dark", offvalue="light",
                                         command=lambda: ctk.set_appearance_mode(theme_switch.get()))
            theme_switch.place(x=12, y=146)
            if settings.get("theme", "dark") == "dark":
                theme_switch.select()
            else:
                theme_switch.deselect()

            save_label = ctk.CTkLabel(f, text="", font=self.font_small)
            save_label.place(x=12, y=200)

            def save_all():
                try:
                    budget_val = float(budget_entry.get().replace(",", "."))
                    if budget_val <= 0:
                        raise ValueError("Budżet musi być > 0")
                    new_settings = {
                        "monthly_budget": budget_val,
                        "theme": theme_switch.get(),
                        "currency": "zł"
                    }
                    save_settings(new_settings)
                    ctk.set_appearance_mode(theme_switch.get())
                    save_label.configure(text="✅ Zapisano!", text_color=KOLORY["success"])
                    f.after(2000, lambda: save_label.configure(text=""))
                except ValueError as e:
                    save_label.configure(text=f"❌ {e}", text_color=KOLORY["danger"])

            ctk.CTkButton(f, text="💾 Zapisz ustawienia", width=200, height=38,
                          fg_color=KOLORY["primary"], font=self.font_mid_b,
                          command=save_all).place(x=12, y=168)

            # right_top – informacje
            f = self.frames["right_top"]
            ctk.CTkLabel(f, text="ℹ️ O aplikacji", font=self.font_label,
                         text_color=KOLORY["text_dim"]).place(x=12, y=8)
            ctk.CTkLabel(f, text="💰 BudżetApp", font=self.font_big).place(x=12, y=38)
            ctk.CTkLabel(f, text="Aplikacja do zarządzania budżetem domowym\nwersja 1.0 • Python + CustomTkinter",
                         font=self.font_small, text_color=KOLORY["text_dim"], justify="left").place(x=12, y=80)

            transactions = load_transactions()
            goals = load_goals()
            ctk.CTkLabel(f, text=f"📊 Transakcji w bazie: {len(transactions)}", font=self.font_small).place(x=12, y=140)
            ctk.CTkLabel(f, text=f"🎯 Celów oszczędnościowych: {len(goals)}", font=self.font_small).place(x=12, y=165)
            ctk.CTkLabel(f, text=f"🏷️ Kategorii: {len(load_categories())}", font=self.font_small).place(x=12, y=190)
        except Exception as e:
            print(f"[show_settings] Error: {e}")