import customtkinter as ctk
from datetime import date
import calendar
import json
import os

# Importy naszych modułów – funkcje używane w różnych panelach
from logic import (
    get_monthly_summary,
    get_today_budget,
    format_currency,
    forecast_month,
    get_savings_progress,
    get_category_breakdown,
)
from charts import DailyBudgetGauge, CategoryPieChart, DailyBarChart, MonthCompareChart
from data_manager import (
    load_transactions,
    load_categories,
    load_goals,
    add_transaction,
    delete_transaction,
    save_goals,
)


class PanelManager:
    def __init__(self, frames: dict):
        """
        frames: słownik z referencjami do ramek:
            {"left_top": CTkFrame, "right_top": CTkFrame, "left_bottom": CTkFrame,
             "right_bottom": CTkFrame, "bottom": CTkFrame, "right": CTkFrame}
        """
        self.frames = frames
        self.current_panel = "dashboard"
        self._nav_buttons = {}
        self._setup_fonts()
        self.show_dashboard()

    # ──────────────────────────────────────────────
    #  Wewnętrzne pomocnicze
    # ──────────────────────────────────────────────
    def _setup_fonts(self):
        self.font_big = ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        self.font_mid = ctk.CTkFont(family="Segoe UI", size=14)
        self.font_small = ctk.CTkFont(family="Segoe UI", size=11)
        self.font_label = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")

    def register_nav_buttons(self, buttons: dict):
        """
        buttons: {"dashboard": CTkButton, "transactions": CTkButton, ...}
        """
        self._nav_buttons = buttons
        self._highlight_active("dashboard")

    def _highlight_active(self, active: str):
        for key, btn in self._nav_buttons.items():
            if key == active:
                btn.configure(fg_color="#3B82F6")
            else:
                btn.configure(fg_color="transparent")

    def _clear_all(self):
        for frame in self.frames.values():
            for widget in frame.winfo_children():
                widget.destroy()

    # ──────────────────────────────────────────────
    #  Panel: Dashboard
    # ──────────────────────────────────────────────
    def show_dashboard(self):
        try:
            self._clear_all()
            self.current_panel = "dashboard"
            self._highlight_active("dashboard")

            today = date.today()
            summary = get_monthly_summary(today.year, today.month)
            budget_data = get_today_budget(monthly_budget=3000, year=today.year, month=today.month)
            transactions = load_transactions()

            # Lewa górna – Budżet na dziś
            frame = self.frames["left_top"]
            ctk.CTkLabel(frame, text="💰 Budżet na dziś", font=self.font_label).place(x=10, y=8)
            gauge = DailyBudgetGauge(
                frame,
                remaining=budget_data["remaining_today"],
                daily_budget=budget_data["daily_budget"],
            )
            gauge.place(x=0, y=30, width=360, height=190)

            # Prawa górna – Wydatki miesiąca
            frame = self.frames["right_top"]
            ctk.CTkLabel(frame, text="📉 Wydatki w tym miesiącu", font=self.font_label).place(x=10, y=8)
            ctk.CTkLabel(
                frame,
                text=format_currency(summary["expense"]),
                font=self.font_big,
                text_color="#EF4444",
            ).place(relx=0.5, rely=0.4, anchor="center")

            forecast = forecast_month(today.year, today.month)
            ctk.CTkLabel(
                frame,
                text=f"Prognoza: {format_currency(forecast['forecast_total'])}",
                font=self.font_small,
                text_color="gray60",
            ).place(relx=0.5, rely=0.7, anchor="center")

            # Lewa dolna – Przychody
            frame = self.frames["left_bottom"]
            ctk.CTkLabel(frame, text="📈 Przychody", font=self.font_label).place(x=10, y=8)
            ctk.CTkLabel(
                frame,
                text=format_currency(summary["income"]),
                font=self.font_big,
                text_color="#10B981",
            ).place(relx=0.5, rely=0.4, anchor="center")
            balance_color = "#10B981" if summary["balance"] >= 0 else "#EF4444"
            ctk.CTkLabel(
                frame,
                text=f"Bilans: {format_currency(summary['balance'])}",
                font=self.font_small,
                text_color=balance_color,
            ).place(relx=0.5, rely=0.7, anchor="center")

            # Prawa dolna – Cel oszczędnościowy
            frame = self.frames["right_bottom"]
            ctk.CTkLabel(frame, text="🎯 Cel oszczędnościowy", font=self.font_label).place(x=10, y=8)
            goals = load_goals()
            if goals:
                goal = goals[0]  # pierwszy cel
                progress = get_savings_progress(goal["id"])
                if progress:
                    ctk.CTkLabel(
                        frame,
                        text=goal.get("name", "Mój cel"),
                        font=self.font_mid,
                    ).place(relx=0.5, rely=0.25, anchor="center")

                    pb = ctk.CTkProgressBar(frame, width=300, height=16)
                    pb.place(relx=0.5, rely=0.50, anchor="center")
                    pb.set(progress["percent"] / 100)

                    ctk.CTkLabel(
                        frame,
                        text=f"{format_currency(progress['current'])} / {format_currency(progress['target'])}",
                        font=self.font_small,
                        text_color="gray60",
                    ).place(relx=0.5, rely=0.70, anchor="center")

                    ctk.CTkLabel(
                        frame,
                        text=f"{progress['percent']:.0f}%",
                        font=self.font_big,
                        text_color="#3B82F6",
                    ).place(relx=0.5, rely=0.88, anchor="center")
            else:
                ctk.CTkLabel(
                    frame,
                    text="Brak celów\n\nDodaj cel w zakładce Cele",
                    font=self.font_mid,
                    text_color="gray50",
                ).place(relx=0.5, rely=0.5, anchor="center")

            # Dolny pasek – wykres słupkowy dzienny
            frame = self.frames["bottom"]
            ctk.CTkLabel(frame, text="📊 Wydatki dzienne w tym miesiącu", font=self.font_label).place(x=10, y=5)
            bar = DailyBarChart(
                frame,
                transactions=transactions,
                daily_limit=budget_data["daily_budget"],
            )
            bar.place(x=0, y=28, width=735, height=137)

            # Prawy panel boczny – wykres kołowy kategorii
            frame = self.frames["right"]
            ctk.CTkLabel(frame, text="Kategorie", font=self.font_label).place(relx=0.5, y=8, anchor="n")
            cat_data = get_category_breakdown(today.year, today.month)
            pie = CategoryPieChart(frame, data=cat_data)
            pie.place(x=0, y=30, width=300, height=595)

        except Exception as e:
            print(f"Panel error (dashboard): {e}")

    # ──────────────────────────────────────────────
    #  Panel: Transakcje
    # ──────────────────────────────────────────────
    def show_transactions(self):
        try:
            self._clear_all()
            self.current_panel = "transactions"
            self._highlight_active("transactions")

            today = date.today()
            summary = get_monthly_summary(today.year, today.month)

            # Lewa górna – nagłówek + przycisk dodaj
            frame = self.frames["left_top"]
            ctk.CTkLabel(frame, text="📋 Transakcje", font=self.font_label).place(x=10, y=8)
            add_btn = ctk.CTkButton(
                frame,
                text="+ Dodaj",
                width=100,
                height=32,
                fg_color="#10B981",
                command=lambda: self._open_add_transaction_form(),
            )
            add_btn.place(x=240, y=8)

            # Prawa górna – podsumowanie miesiąca
            frame = self.frames["right_top"]
            ctk.CTkLabel(frame, text="Przychody:", font=self.font_small).place(x=10, y=30)
            ctk.CTkLabel(
                frame,
                text=format_currency(summary["income"]),
                text_color="#10B981",
                font=self.font_mid,
            ).place(x=100, y=30)

            ctk.CTkLabel(frame, text="Wydatki:", font=self.font_small).place(x=10, y=70)
            ctk.CTkLabel(
                frame,
                text=format_currency(summary["expense"]),
                text_color="#EF4444",
                font=self.font_mid,
            ).place(x=100, y=70)

            ctk.CTkLabel(frame, text="Bilans:", font=self.font_small).place(x=10, y=110)
            balance_color = "#10B981" if summary["balance"] >= 0 else "#EF4444"
            ctk.CTkLabel(
                frame,
                text=format_currency(summary["balance"]),
                text_color=balance_color,
                font=self.font_mid,
            ).place(x=100, y=110)

            # Dolne ramki – lista transakcji
            # Użyjemy lewej dolnej jako scrollowalnego kontenera, ale rozciągniemy go na całą dostępną przestrzeń.
            # Ponieważ mamy wiele ramek (left_bottom, right_bottom, bottom), można zrobić jeden duży scroll
            # w left_bottom i ukryć pozostałe lub połączyć. Najprościej: zignorować right_bottom i bottom,
            # a całą listę umieścić w left_bottom (360x220) – to za mało, więc rozszerzamy obszar.
            # Możemy wykorzystać bottom (735x165) jako kontynuację, ale lepiej zrobić scroll obejmujący
            # left_bottom + right_bottom + bottom. Aby to osiągnąć, tworzymy scroll w self.frames["left_bottom"],
            # ale ustawiamy go na dużą wysokość (np. 220+220+165 = 605) i umieszczamy w lewym dolnym,
            # ale wyjdzie poza ramkę (nie będzie widoczny). Lepsze: Stworzyć tymczasową ramkę
            # w głównym oknie? Ramki są stałe, więc najprościej użyć left_bottom jako scroll
            # i przewijać tylko tę część, a resztę ramek zostawić pustą. Ale w specyfikacji mowa
            # o użyciu left_bottom + right_bottom + bottom. Możemy umieścić scroll w left_bottom
            # i rozciągnąć go na całą dostępną wysokość (wykorzystując place, ale parent to left_bottom,
            # więc rozmiar ograniczony do 220). Alternatywnie, można wstawić scroll do left_bottom,
            # a w right_bottom i bottom nic nie dawać. Zróbmy tak: scroll w left_bottom z height=200,
            # a pozostałe ramki zostawimy puste. To zgodne z opisem: „RAMKA left_bottom + right_bottom + bottom — lista transakcji jako CTkScrollableFrame:
            # Utwórz CTkScrollableFrame w self.frames["left_bottom"]”. Tak więc reszta pozostanie pusta.
            scroll = ctk.CTkScrollableFrame(
                self.frames["left_bottom"],
                width=340,
                height=200,
            )
            scroll.place(x=0, y=0)

            transactions = sorted(load_transactions(), key=lambda t: t["date"], reverse=True)
            categories = {c["id"]: c for c in load_categories()}

            # Wyświetlamy maksymalnie 50 transakcji
            for idx, t in enumerate(transactions[:50]):
                row_frame = ctk.CTkFrame(
                    scroll,
                    height=38,
                    fg_color="#1e1e2e" if idx % 2 == 0 else "transparent",
                )
                row_frame.pack(fill="x", padx=2, pady=1)

                cat = categories.get(
                    t["category_id"],
                    {"icon": "?", "name": "Nieznana", "color": "gray"},
                )
                color = "#10B981" if t["type"] == "income" else "#EF4444"
                sign = "+" if t["type"] == "income" else "-"

                ctk.CTkLabel(row_frame, text=t["date"][5:], width=50, font=self.font_small).place(x=2, y=10)
                ctk.CTkLabel(
                    row_frame,
                    text=f"{cat['icon']} {cat['name']}",
                    width=120,
                    font=self.font_small,
                ).place(x=52, y=10)
                ctk.CTkLabel(
                    row_frame,
                    text=t.get("description", "")[:20],
                    font=self.font_small,
                ).place(x=175, y=10)
                ctk.CTkLabel(
                    row_frame,
                    text=f"{sign}{format_currency(t['amount'])}",
                    text_color=color,
                    font=self.font_small,
                    width=100,
                ).place(x=230, y=10)
                del_btn = ctk.CTkButton(
                    row_frame,
                    text="🗑",
                    width=28,
                    height=24,
                    fg_color="transparent",
                    command=lambda tid=t["id"]: self._delete_transaction(tid),
                )
                del_btn.place(x=332, y=7)

        except Exception as e:
            print(f"Panel error (transactions): {e}")

    def _open_add_transaction_form(self):
        try:
            dialog = ctk.CTkToplevel()
            dialog.title("Dodaj transakcję")
            dialog.geometry("320x360")
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="Nowa transakcja", font=self.font_label).pack(pady=10)

            # Typ transakcji
            type_var = ctk.StringVar(value="expense")
            type_seg = ctk.CTkSegmentedButton(
                dialog,
                values=["💸 Wydatek", "💰 Przychód"],
                variable=type_var,
            )
            type_seg.pack(pady=10)

            # Kwota
            ctk.CTkLabel(dialog, text="Kwota (zł):").pack()
            amount_entry = ctk.CTkEntry(dialog, placeholder_text="np. 49.99")
            amount_entry.pack(pady=5)

            # Kategoria
            ctk.CTkLabel(dialog, text="Kategoria:").pack()
            categories = load_categories()
            # Filtruj kategorie zgodnie z typem? Możemy dać wszystkie.
            cat_options = [f"{c['icon']} {c['name']}" for c in categories]
            cat_var = ctk.StringVar(value=cat_options[0] if cat_options else "")
            cat_menu = ctk.CTkOptionMenu(dialog, values=cat_options, variable=cat_var)
            cat_menu.pack(pady=5)

            # Data
            ctk.CTkLabel(dialog, text="Data (YYYY-MM-DD):").pack()
            date_entry = ctk.CTkEntry(dialog)
            date_entry.insert(0, date.today().isoformat())
            date_entry.pack(pady=5)

            # Opis
            ctk.CTkLabel(dialog, text="Opis:").pack()
            desc_entry = ctk.CTkEntry(dialog)
            desc_entry.pack(pady=5)

            def save_transaction():
                try:
                    amount_str = amount_entry.get().replace(",", ".")
                    amount = float(amount_str)
                    if amount <= 0:
                        raise ValueError("Kwota musi być dodatnia")

                    # Określenie typu na podstawie przycisku
                    if "Przychód" in type_var.get():
                        trans_type = "income"
                    else:
                        trans_type = "expense"

                    # Wyciągnięcie id kategorii
                    selected_cat_name = cat_var.get()
                    cat_id = None
                    for c in categories:
                        if f"{c['icon']} {c['name']}" == selected_cat_name:
                            cat_id = c["id"]
                            break
                    if cat_id is None:
                        raise ValueError("Nie wybrano kategorii")

                    date_str = date_entry.get().strip()
                    desc = desc_entry.get().strip()

                    add_transaction(
                        amount=amount,
                        type=trans_type,
                        category_id=cat_id,
                        description=desc,
                        date_str=date_str,
                    )
                    dialog.destroy()
                    self.show_transactions()  # odświeżenie
                except ValueError as ve:
                    # Wyświetl błąd (można wstawić label z błędem, na razie print)
                    print(f"Błąd walidacji: {ve}")

            ctk.CTkButton(dialog, text="Zapisz", command=save_transaction).pack(pady=15)
            ctk.CTkButton(dialog, text="Anuluj", command=dialog.destroy).pack()

        except Exception as e:
            print(f"Błąd otwierania formularza transakcji: {e}")

    def _delete_transaction(self, transaction_id: int):
        try:
            delete_transaction(transaction_id)
            self.show_transactions()
        except Exception as e:
            print(f"Błąd usuwania transakcji: {e}")

    # ──────────────────────────────────────────────
    #  Panel: Cele oszczędnościowe
    # ──────────────────────────────────────────────
    def show_goals(self):
        try:
            self._clear_all()
            self.current_panel = "goals"
            self._highlight_active("goals")

            # Lewa górna – nagłówek + przycisk nowy cel
            frame = self.frames["left_top"]
            ctk.CTkLabel(frame, text="🎯 Cele oszczędnościowe", font=self.font_label).place(x=10, y=8)
            ctk.CTkButton(
                frame,
                text="+ Nowy cel",
                width=110,
                height=32,
                fg_color="#3B82F6",
                command=lambda: self._open_add_goal_form(),
            ).place(x=230, y=8)

            goals = load_goals()
            # Wyświetlamy karty celów na lewej dolnej i prawej dolnej ramce
            for i, goal in enumerate(goals):
                col = i % 2
                frame_key = "left_bottom" if col == 0 else "right_bottom"
                f = self.frames[frame_key]
                offset_y = (i // 2) * 110

                card = ctk.CTkFrame(f, width=340, height=100, corner_radius=10)
                card.place(x=10, y=offset_y + 10)

                ctk.CTkLabel(card, text=goal["name"], font=self.font_mid).place(x=10, y=8)
                pb = ctk.CTkProgressBar(card, width=280, height=12)
                pb.place(x=10, y=40)

                current = goal.get("current_amount", 0)
                target = goal.get("target_amount", 1)
                pb.set(min(1.0, current / target))

                ctk.CTkLabel(
                    card,
                    text=f"{format_currency(current)} / {format_currency(target)}",
                    font=self.font_small,
                    text_color="gray60",
                ).place(x=10, y=60)

                deposit_btn = ctk.CTkButton(
                    card,
                    text="+ Wpłata",
                    width=80,
                    height=24,
                    fg_color="#10B981",
                    command=lambda gid=goal["id"]: self._add_deposit(gid),
                )
                deposit_btn.place(x=255, y=70)

            # Jeżeli brak celów, można wyświetlić informację w lewej dolnej
            if not goals:
                f = self.frames["left_bottom"]
                ctk.CTkLabel(f, text="Nie masz jeszcze żadnych celów.", font=self.font_mid).place(relx=0.5, rely=0.5, anchor="center")

        except Exception as e:
            print(f"Panel error (goals): {e}")

    def _open_add_goal_form(self):
        try:
            dialog = ctk.CTkToplevel()
            dialog.title("Nowy cel")
            dialog.geometry("300x230")
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="Nazwa celu:").pack(pady=5)
            name_entry = ctk.CTkEntry(dialog, placeholder_text="np. Wakacje")
            name_entry.pack(pady=5)

            ctk.CTkLabel(dialog, text="Kwota docelowa (zł):").pack(pady=5)
            target_entry = ctk.CTkEntry(dialog, placeholder_text="np. 5000")
            target_entry.pack(pady=5)

            def save_goal():
                try:
                    name = name_entry.get().strip()
                    target = float(target_entry.get().replace(",", "."))
                    if not name or target <= 0:
                        raise ValueError("Nieprawidłowe dane")

                    goals = load_goals()
                    new_id = max((g["id"] for g in goals), default=0) + 1
                    new_goal = {
                        "id": new_id,
                        "name": name,
                        "target_amount": target,
                        "current_amount": 0.0,
                        "color": "#3B82F6",  # domyślny kolor
                    }
                    goals.append(new_goal)
                    save_goals(goals)
                    dialog.destroy()
                    self.show_goals()
                except ValueError as ve:
                    print(f"Błąd dodawania celu: {ve}")

            ctk.CTkButton(dialog, text="Zapisz", command=save_goal).pack(pady=10)
            ctk.CTkButton(dialog, text="Anuluj", command=dialog.destroy).pack()

        except Exception as e:
            print(f"Błąd otwierania formularza celu: {e}")

    def _add_deposit(self, goal_id):
        try:
            dialog = ctk.CTkToplevel()
            dialog.title("Wpłata na cel")
            dialog.geometry("250x150")
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="Kwota wpłaty (zł):").pack(pady=10)
            amount_entry = ctk.CTkEntry(dialog, placeholder_text="np. 200")
            amount_entry.pack(pady=5)

            def deposit():
                try:
                    amount = float(amount_entry.get().replace(",", "."))
                    if amount <= 0:
                        raise ValueError("Kwota musi być dodatnia")

                    goals = load_goals()
                    for g in goals:
                        if g["id"] == goal_id:
                            g["current_amount"] = g.get("current_amount", 0) + amount
                            break
                    save_goals(goals)
                    dialog.destroy()
                    self.show_goals()
                except ValueError as ve:
                    print(f"Błąd wpłaty: {ve}")

            ctk.CTkButton(dialog, text="Wpłać", command=deposit).pack(pady=5)
            ctk.CTkButton(dialog, text="Anuluj", command=dialog.destroy).pack()

        except Exception as e:
            print(f"Błąd otwierania wpłaty: {e}")

    # ──────────────────────────────────────────────
    #  Panel: Raporty
    # ──────────────────────────────────────────────
    def show_reports(self):
        try:
            self._clear_all()
            self.current_panel = "reports"
            self._highlight_active("reports")

            today = date.today()

            # Lewa górna – nagłówek
            frame = self.frames["left_top"]
            ctk.CTkLabel(frame, text="📈 Raporty", font=self.font_label).place(x=10, y=8)

            # Zbierz dane z ostatnich 6 miesięcy
            months_data = []
            for i in range(5, -1, -1):
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                summary = get_monthly_summary(y, m)
                month_names = [
                    "Sty", "Lut", "Mar", "Kwi", "Maj", "Cze",
                    "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru",
                ]
                months_data.append({
                    "label": month_names[m - 1],
                    "income": summary["income"],
                    "expense": summary["expense"],
                })

            # Prawa górna – wykres porównawczy
            frame = self.frames["right_top"]
            compare = MonthCompareChart(frame, months_data=months_data)
            compare.place(x=0, y=0, width=360, height=220)

            # Dolny pasek – podsumowanie
            frame = self.frames["bottom"]
            ctk.CTkLabel(frame, text="Podsumowanie 6 miesięcy", font=self.font_label).place(x=10, y=5)

            total_income = sum(m["income"] for m in months_data)
            total_expense = sum(m["expense"] for m in months_data)

            ctk.CTkLabel(
                frame,
                text=f"Łączne przychody: {format_currency(total_income)}",
                text_color="#10B981",
                font=self.font_mid,
            ).place(x=20, y=40)

            ctk.CTkLabel(
                frame,
                text=f"Łączne wydatki: {format_currency(total_expense)}",
                text_color="#EF4444",
                font=self.font_mid,
            ).place(x=20, y=80)

            ctk.CTkLabel(
                frame,
                text=f"Oszczędności: {format_currency(total_income - total_expense)}",
                font=self.font_mid,
            ).place(x=20, y=120)

        except Exception as e:
            print(f"Panel error (reports): {e}")

    # ──────────────────────────────────────────────
    #  Panel: Kategorie
    # ──────────────────────────────────────────────
    def show_categories(self):
        try:
            self._clear_all()
            self.current_panel = "categories"
            self._highlight_active("categories")

            # Lewa górna – nagłówek
            frame = self.frames["left_top"]
            ctk.CTkLabel(frame, text="🏷️ Kategorie", font=self.font_label).place(x=10, y=8)

            # Lewa dolna – lista kategorii
            frame = self.frames["left_bottom"]
            cats = load_categories()
            scroll = ctk.CTkScrollableFrame(frame, width=340, height=200)
            scroll.place(x=0, y=0)

            for cat in cats:
                row = ctk.CTkFrame(scroll, height=36, fg_color="transparent")
                row.pack(fill="x", pady=1)

                ctk.CTkLabel(
                    row,
                    text=f"{cat['icon']} {cat['name']}",
                    font=self.font_small,
                    width=200,
                ).place(x=5, y=8)

                type_label = "wydatek" if cat["type"] == "expense" else "przychód"
                ctk.CTkLabel(
                    row,
                    text=type_label,
                    font=self.font_small,
                    text_color="gray50",
                ).place(x=210, y=8)

                # Kwadracik z kolorem kategorii
                color_box = ctk.CTkFrame(
                    row,
                    width=16,
                    height=16,
                    fg_color=cat.get("color", "gray"),
                    corner_radius=3,
                )
                color_box.place(x=305, y=10)

        except Exception as e:
            print(f"Panel error (categories): {e}")

    # ──────────────────────────────────────────────
    #  Panel: Ustawienia
    # ──────────────────────────────────────────────
    def show_settings(self):
        try:
            self._clear_all()
            self.current_panel = "settings"
            self._highlight_active("settings")

            frame = self.frames["left_top"]
            ctk.CTkLabel(frame, text="⚙️ Ustawienia", font=self.font_label).place(x=10, y=8)

            ctk.CTkLabel(frame, text="Miesięczny budżet (zł):", font=self.font_small).place(x=10, y=50)
            budget_entry = ctk.CTkEntry(frame, width=180, placeholder_text="np. 3000")
            budget_entry.place(x=10, y=75)
            # Wczytaj zapisany budżet, jeśli istnieje
            try:
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
                    saved_budget = settings.get("monthly_budget", "")
                    budget_entry.insert(0, str(saved_budget))
            except Exception:
                pass

            ctk.CTkLabel(frame, text="Motyw:", font=self.font_small).place(x=10, y=115)
            theme_switch = ctk.CTkSwitch(
                frame,
                text="Ciemny motyw",
                command=lambda: ctk.set_appearance_mode(
                    "dark" if theme_switch.get() else "light"
                ),
            )
            theme_switch.place(x=10, y=140)
            theme_switch.select()  # domyślnie ciemny

            ctk.CTkButton(
                frame,
                text="💾 Zapisz",
                width=150,
                command=lambda: self._save_settings(budget_entry.get()),
            ).place(x=10, y=190)

        except Exception as e:
            print(f"Panel error (settings): {e}")

    def _save_settings(self, budget_str: str):
        try:
            budget = float(budget_str.replace(",", "."))
            if not os.path.exists("data"):
                os.makedirs("data")
            with open("data/settings.json", "w") as f:
                json.dump({"monthly_budget": budget}, f)
            # Komunikat – można pokazać tymczasowy label, na razie print
            print("Ustawienia zapisane.")
        except ValueError:
            print("Nieprawidłowa kwota budżetu.")
        except Exception as e:
            print(f"Błąd zapisu ustawień: {e}")