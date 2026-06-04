import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import calendar

# Styl dark – ustawiany jednorazowo na początku
plt.rcParams.update({
    "text.color": "#e0e0e0",
    "axes.labelcolor": "#e0e0e0",
    "xtick.color": "#aaaaaa",
    "ytick.color": "#aaaaaa",
})


class DailyBudgetGauge(ctk.CTkFrame):
    """Termometr – pionowy pasek pokazujący pozostały budżet dzienny."""

    def __init__(self, master, remaining, daily_budget, **kwargs):
        super().__init__(master, **kwargs)

        self.remaining = remaining
        self.daily_budget = daily_budget

        self.fig = Figure(figsize=(3.2, 2.0), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        self._draw_gauge()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        # Tło canvasu dopasowane do koloru ramki
        bg_color = self.cget("fg_color")
        if isinstance(bg_color, tuple):
            bg_color = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        self.canvas.get_tk_widget().configure(background=bg_color)

    def _draw_gauge(self):
        self.ax.clear()
        self.ax.set_facecolor("none")
        self.ax.axis("off")

        # Słupek tła (całość daily_budget)
        self.ax.barh(0, self.daily_budget, color="gray", alpha=0.3, height=0.4)

        # Kolor wypełnienia
        if self.remaining < 0:
            fill_color = "#EF4444"
            fill_value = self.daily_budget   # pokazujemy cały pasek jako sygnał przekroczenia
        else:
            ratio = self.remaining / self.daily_budget if self.daily_budget else 0
            if ratio >= 0.3:
                fill_color = "#10B981"
            else:
                fill_color = "#F59E0B"
            fill_value = min(self.remaining, self.daily_budget)

        self.ax.barh(0, fill_value, color=fill_color, height=0.4)

        # Formatowanie pozostałej kwoty
        formatted = f"{self.remaining:,.2f} zł".replace(",", " ").replace(".", ",")
        self.ax.set_title(f"Pozostało dziś\n{formatted}", fontsize=11, fontweight="bold", pad=10)

        # Duża kwota na środku
        self.ax.text(0.5, 0.5, formatted,
                     transform=self.ax.transAxes, ha="center", va="center",
                     fontsize=14, fontweight="bold", color="white")

    def update(self, remaining, daily_budget):
        self.remaining = remaining
        self.daily_budget = daily_budget
        self._draw_gauge()
        self.canvas.draw_idle()

    def destroy(self):
        plt.close(self.fig)
        super().destroy()


class CategoryPieChart(ctk.CTkFrame):
    """Wykres kołowy wydatków wg kategorii."""

    def __init__(self, master, data: list, **kwargs):
        super().__init__(master, **kwargs)

        self.data = data
        self.fig = Figure(figsize=(2.8, 2.8), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        self._draw_pie()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        bg_color = self.cget("fg_color")
        if isinstance(bg_color, tuple):
            bg_color = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        self.canvas.get_tk_widget().configure(background=bg_color)

    def _draw_pie(self):
        self.ax.clear()
        self.ax.set_facecolor("none")

        if not self.data:
            self.ax.text(0.5, 0.5, "Brak danych",
                         transform=self.ax.transAxes, ha="center", va="center",
                         fontsize=12, color="#aaaaaa")
            self.ax.axis("off")
            return

        sizes = [item["total"] for item in self.data]
        colors = [item["color"] for item in self.data]
        labels = [f"{item['icon']} {item['name']}" for item in self.data]

        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=None,          # legenda osobno
            colors=colors,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"linewidth": 2, "edgecolor": "none"},
            pctdistance=0.75
        )
        # Poprawa koloru autopct
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(8)

        # Legenda z prawej strony
        self.ax.legend(
            wedges, labels,
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=7,
            frameon=False
        )
        self.fig.subplots_adjust(right=0.7)   # miejsce na legendę

        self.ax.axis("off")

    def update(self, data: list):
        self.data = data
        self._draw_pie()
        self.canvas.draw_idle()

    def destroy(self):
        plt.close(self.fig)
        super().destroy()


class DailyBarChart(ctk.CTkFrame):
    """Słupkowy wykres dziennych wydatków w bieżącym miesiącu."""

    def __init__(self, master, transactions: list, daily_limit: float, **kwargs):
        super().__init__(master, **kwargs)

        self.transactions = transactions
        self.daily_limit = daily_limit
        self.fig = Figure(figsize=(6.5, 1.5), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        self._draw_bars()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        bg_color = self.cget("fg_color")
        if isinstance(bg_color, tuple):
            bg_color = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        self.canvas.get_tk_widget().configure(background=bg_color)

    def _draw_bars(self):
        self.ax.clear()
        self.ax.set_facecolor("none")

        today = datetime.date.today()
        days = range(1, today.day + 1) if today.month else []

        # Zliczanie wydatków per dzień
        daily_expenses = {d: 0.0 for d in days}
        for t in self.transactions:
            if t["type"] == "expense":
                try:
                    trans_date = datetime.date.fromisoformat(t["date"])
                    if (trans_date.year == today.year and
                        trans_date.month == today.month and
                        1 <= trans_date.day <= today.day):
                        daily_expenses[trans_date.day] += t["amount"]
                except (ValueError, KeyError):
                    continue

        day_nums = list(daily_expenses.keys())
        amounts = list(daily_expenses.values())
        colors = ["#10B981" if amt < self.daily_limit else "#EF4444" for amt in amounts]

        self.ax.bar(day_nums, amounts, color=colors, alpha=0.8, width=0.6)
        self.ax.axhline(y=self.daily_limit, color="#F59E0B", linestyle="--",
                        linewidth=1, label=f"Dzienny limit ({self.daily_limit:.2f})")
        self.ax.set_xlabel("Dzień", fontsize=7)
        self.ax.set_ylabel("Wydatki (zł)", fontsize=7)
        self.ax.tick_params(axis='both', labelsize=7)
        self.ax.legend(fontsize=7, frameon=False)

        # Usuń zbędne elementy
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

    def update(self, transactions: list, daily_limit: float):
        self.transactions = transactions
        self.daily_limit = daily_limit
        self._draw_bars()
        self.canvas.draw_idle()

    def destroy(self):
        plt.close(self.fig)
        super().destroy()


class MonthCompareChart(ctk.CTkFrame):
    """Zgrupowany wykres słupkowy przychodów i wydatków w kolejnych miesiącach."""

    def __init__(self, master, months_data: list, **kwargs):
        super().__init__(master, **kwargs)

        self.months_data = months_data
        self.fig = Figure(figsize=(2.5, 2.5), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        self._draw_comparison()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        bg_color = self.cget("fg_color")
        if isinstance(bg_color, tuple):
            bg_color = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        self.canvas.get_tk_widget().configure(background=bg_color)

    def _draw_comparison(self):
        self.ax.clear()
        self.ax.set_facecolor("none")

        if not self.months_data:
            self.ax.text(0.5, 0.5, "Brak danych",
                         transform=self.ax.transAxes, ha="center", va="center",
                         fontsize=10, color="#aaaaaa")
            self.ax.axis("off")
            return

        labels = [m["label"] for m in self.months_data]
        incomes = [m["income"] for m in self.months_data]
        expenses = [m["expense"] for m in self.months_data]
        x = range(len(labels))
        width = 0.35

        bars_inc = self.ax.bar([i - width/2 for i in x], incomes, width,
                               color="#10B981", label="Przychody")
        bars_exp = self.ax.bar([i + width/2 for i in x], expenses, width,
                               color="#EF4444", label="Wydatki")

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels, fontsize=8)
        self.ax.tick_params(axis='y', labelsize=8)
        self.ax.legend(loc='upper center', fontsize=8, frameon=False, ncol=2,
                       bbox_to_anchor=(0.5, 1.15))

        # Usuń ramkę
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.tick_params(bottom=False)

    def update(self, months_data: list):
        self.months_data = months_data
        self._draw_comparison()
        self.canvas.draw_idle()

    def destroy(self):
        plt.close(self.fig)
        super().destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x400")
    ctk.set_appearance_mode("dark")

    test_data = [
        {"name": "Jedzenie", "color": "#EF4444", "total": 450, "icon": "🍔"},
        {"name": "Transport", "color": "#F59E0B", "total": 120, "icon": "🚗"},
        {"name": "Rozrywka", "color": "#EC4899", "total": 200, "icon": "🎮"},
    ]
    frame = CategoryPieChart(root, data=test_data)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()