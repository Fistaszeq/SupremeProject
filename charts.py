from gui import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import date
import calendar
import math

plt.rcParams.update({
    "text.color": "#c8c8d4",
    "axes.labelcolor": "#c8c8d4",
    "xtick.color": "#888899",
    "ytick.color": "#888899",
    "axes.edgecolor": "#3a3a4a",
    "grid.color": "#2a2a3a",
    "grid.alpha": 0.5,
    "font.family": "Segoe UI",
})
DARK_BG = "#1e1e2e"
CARD_BG = "#252535"

THEMES = {
    "dark": {
        "bg": DARK_BG,
        "card_bg": CARD_BG,
        "text": "#c8c8d4",
        "muted": "#888899",
        "axes_edge": "#3a3a4a",
        "grid": "#2a2a3a",
        "contrast_text": "white",
    },
    "light": {
        "bg": "#ffffff",
        "card_bg": "#f3f4f6",
        "text": "#1f2937",
        "muted": "#6b7280",
        "axes_edge": "#e5e7eb",
        "grid": "#e6e6e6",
        "contrast_text": "#111827",
    },
}

def _is_dark_mode():
    try:
        mode = ctk.get_appearance_mode()
        return str(mode).lower().startswith("d")
    except Exception:
        return True

def _theme():
    return THEMES["dark"] if _is_dark_mode() else THEMES["light"]


class DonutChart(ctk.CTkFrame):
    def __init__(self, master, percent: float, label: str, color: str, **kwargs):
        self.percent = percent
        self.label = label
        self.color = color
        self.fig = plt.Figure(figsize=(2.2, 2.2), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        super().__init__(master, **kwargs)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        try:
            self.canvas.get_tk_widget().configure(bg=self._apply_appearance_mode(self._fg_color))
        except Exception:
            pass
        self._draw()
        self.canvas.draw()

    def _draw(self, *args, **kwargs):
        self.ax.clear()
        # set background for axes according to theme
        th = _theme()
        self.ax.set_facecolor("none")
        p = max(0.0, min(100.0, self.percent))
        self.ax.pie(
            [p, 100 - p],
            colors=[self.color, "#2a2a3a"],
            startangle=90,
            wedgeprops={"width": 0.35, "linewidth": 0},
        )
        self.ax.text(
            0, 0, f"{p:.0f}%",
            ha="center", va="center",
            fontsize=16, fontweight="bold", color=th["contrast_text"],
        )
        self.ax.set_title(self.label, fontsize=8, color=th["muted"], pad=2)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def update(self, percent: float, label: str):
        self.percent = percent
        self.label = label
        self._draw()
        self.canvas.draw_idle()

    def destroy(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        super().destroy()


class SpendingBarChart(ctk.CTkFrame):
    def __init__(self, master, data: list, **kwargs):
        self.data = data
        self.fig = plt.Figure(figsize=(3.0, 3.5), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        super().__init__(master, **kwargs)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        try:
            self.canvas.get_tk_widget().configure(bg=self._apply_appearance_mode(self._fg_color))
        except Exception:
            pass
        self._draw()
        self.canvas.draw()

    def _draw(self, *args, **kwargs):
        self.ax.clear()
        th = _theme()
        try:
            self.ax.set_facecolor(self._apply_appearance_mode(self._fg_color))
        except Exception:
            self.ax.set_facecolor(th["bg"])

        if not self.data:
            self.ax.text(
                0.5, 0.5, "Brak danych w tym miesiącu",
                ha="center", va="center", fontsize=10, color="#888899",
                transform=self.ax.transAxes,
            )
            self.ax.axis("off")
            return

        items = self.data[:7]
        labels = [f"{d['icon']} {d['name']}" for d in items]
        values = [d["total"] for d in items]
        colors = [d["color"] for d in items]
        y_pos = range(len(labels))

        self.ax.barh(y_pos, values, color=colors, alpha=0.85, height=0.65, edgecolor="none")
        self.ax.set_yticks(y_pos)
        self.ax.set_yticklabels(labels, fontsize=9, color=th["text"])
        self.ax.invert_yaxis()

        for spine in self.ax.spines.values():
            spine.set_visible(False)

        max_val = max(values) if values else 1
        for i, v in enumerate(values):
            self.ax.text(v + max_val * 0.02, i, f"{v:.0f} zł",
                         va="center", fontsize=8, color=th["text"])

        self.ax.set_xlim(0, max_val * 1.25)
        self.ax.tick_params(left=False, bottom=False, colors=th["muted"]) 
        self.ax.xaxis.set_visible(False)
        self.fig.tight_layout(pad=0.5)

    def update(self, data: list):
        self.data = data
        self._draw()
        self.canvas.draw_idle()

    def destroy(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        super().destroy()


class MonthTrendChart(ctk.CTkFrame):
    def __init__(self, master, months_data: list, **kwargs):
        self.months_data = months_data
        self.fig = plt.Figure(figsize=(6.5, 2.8), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        super().__init__(master, **kwargs)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        try:
            self.canvas.get_tk_widget().configure(bg=self._apply_appearance_mode(self._fg_color))
        except Exception:
            pass
        self._draw()
        self.canvas.draw()

    def _draw(self, *args, **kwargs):
        self.ax.clear()
        th = _theme()
        try:
            self.ax.set_facecolor(self._apply_appearance_mode(self._fg_color))
        except Exception:
            self.ax.set_facecolor(th["bg"])

        if not self.months_data:
            self.ax.text(0.5, 0.5, "Brak danych", ha="center", va="center",
                         fontsize=10, color="#888899", transform=self.ax.transAxes)
            self.ax.axis("off")
            return

        n = len(self.months_data)
        x = np.arange(n)
        width = 0.3

        incomes = [m["income"] for m in self.months_data]
        expenses = [m["expense"] for m in self.months_data]
        balances = [m["balance"] for m in self.months_data]

        self.ax.bar(x - width/2, incomes, width, color="#10B981", alpha=0.85, label="Przychody", linewidth=0)
        self.ax.bar(x + width/2, expenses, width, color="#EF4444", alpha=0.85, label="Wydatki", linewidth=0)
        self.ax.plot(x, balances, color="#3B82F6", linewidth=2, marker="o", markersize=5, label="Bilans", zorder=5)

        self.ax.set_xticks(x)
        self.ax.set_xticklabels([m["label"] for m in self.months_data], fontsize=9, color=th["text"])
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        for s in ["left", "bottom"]:
            self.ax.spines[s].set_color(th["axes_edge"])
        self.ax.axhline(0, color=th["axes_edge"], linewidth=1, linestyle="--")
        self.ax.legend(fontsize=8, facecolor=th["card_bg"], edgecolor="none", labelcolor=th["text"], loc="upper left")
        self.fig.tight_layout(pad=0.5)

    def update(self, months_data: list):
        self.months_data = months_data
        self._draw()
        self.canvas.draw_idle()

    def destroy(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        super().destroy()


class DailySpendingChart(ctk.CTkFrame):
    def __init__(self, master, transactions: list, daily_limit: float, **kwargs):
        self.transactions = transactions
        self.daily_limit = daily_limit
        self.fig = plt.Figure(figsize=(7.0, 1.8), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        super().__init__(master, **kwargs)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        try:
            self.canvas.get_tk_widget().configure(bg=self._apply_appearance_mode(self._fg_color))
        except Exception:
            pass
        self._draw()
        self.canvas.draw()

    def _draw(self, *args, **kwargs):
        self.ax.clear()
        th = _theme()
        try:
            self.ax.set_facecolor(self._apply_appearance_mode(self._fg_color))
        except Exception:
            self.ax.set_facecolor(th["bg"])

        today = date.today()
        days = list(range(1, today.day + 1))

        daily_totals = []
        for d in days:
            date_str = f"{today.year}-{today.month:02d}-{d:02d}"
            day_sum = sum(
                t["amount"] for t in self.transactions
                if t.get("type") == "expense" and t.get("date") == date_str
            )
            daily_totals.append(day_sum)

        bar_colors = [
            "#10B981" if total <= self.daily_limit else "#EF4444"
            for total in daily_totals
        ]

        self.ax.bar(days, daily_totals, color=bar_colors, alpha=0.85, linewidth=0, width=0.7)
        self.ax.axhline(self.daily_limit, color="#F59E0B", linewidth=1.5,
                        linestyle="--", alpha=0.8, label=f"Limit: {self.daily_limit:.0f} zł")

        self.ax.set_xlim(0.5, max(days) + 0.5 if days else 1)
        if days:
            step = 3 if len(days) > 10 else 1
            ticks = days[::step]
            self.ax.set_xticks(ticks)
            self.ax.set_xticklabels([str(d) for d in ticks], fontsize=8)

        self.ax.tick_params(labelsize=8, colors=th["muted"]) 
        for spine_name in ["top", "right", "left"]:
            self.ax.spines[spine_name].set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.fig.tight_layout(pad=0.3)

    def update(self, transactions: list, daily_limit: float):
        self.transactions = transactions
        self.daily_limit = daily_limit
        self._draw()
        self.canvas.draw_idle()

    def destroy(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        super().destroy()


class GoalProgressRing(ctk.CTkFrame):
    def __init__(self, master, goal: dict, **kwargs):
        super().__init__(master, **kwargs)
        self.goal = goal
        self.percent = min(
            100.0,
            goal["current_amount"] / goal["target_amount"] * 100
            if goal["target_amount"] else 0.0,
        )

        self.fig = plt.Figure(figsize=(1.6, 1.6), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="left", padx=5)
        try:
            self.canvas.get_tk_widget().configure(bg=self._apply_appearance_mode(self._fg_color))
        except Exception:
            pass
        self._draw_ring()
        self.canvas.draw()

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=8, pady=5)

        ctk.CTkLabel(info_frame, text=self.goal.get("name", "Cel"),
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        current = self.goal.get("current_amount", 0.0)
        target = self.goal.get("target_amount", 0.0)
        ctk.CTkLabel(info_frame, text=f"{current:.2f} / {target:.2f} zł",
                     font=ctk.CTkFont(size=10), text_color="gray60").pack(anchor="w")
        missing = target - current
        ctk.CTkLabel(info_frame, text=f"Brakuje: {missing:.2f} zł",
                     font=ctk.CTkFont(size=10),
                     text_color=self.goal.get("color", "#3B82F6")).pack(anchor="w")
        if self.percent >= 100.0:
            ctk.CTkLabel(info_frame, text="🎉 OSIĄGNIĘTO!",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#10B981").pack(anchor="w")

    def _draw_ring(self, *args, **kwargs):
        self.ax.clear()
        th = _theme()
        self.ax.set_facecolor("none")
        p = max(0.0, min(100.0, self.percent))
        self.ax.pie(
            [p, 100 - p],
            colors=[self.goal.get("color", "#3B82F6"), "#2a2a3a"],
            startangle=90,
            wedgeprops={"width": 0.4, "linewidth": 0},
        )
        self.ax.text(0, 0, f"{p:.0f}%", ha="center", va="center",
                 fontsize=12, fontweight="bold", color=th["contrast_text"])
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def destroy(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        super().destroy()


class SavingsLineChart(ctk.CTkFrame):
    def __init__(self, master, current: float, target: float,
                 monthly_saving: float, color: str, **kwargs):
        self.current = current
        self.target = target
        self.monthly_saving = monthly_saving
        self.color = color
        self.fig = plt.Figure(figsize=(3.5, 1.8), facecolor="none")
        self.ax = self.fig.add_subplot(111)
        super().__init__(master, **kwargs)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        try:
            self.canvas.get_tk_widget().configure(bg=self._apply_appearance_mode(self._fg_color))
        except Exception:
            pass
        self._draw()
        self.canvas.draw()

    def _draw(self, *args, **kwargs):
        self.ax.clear()
        try:
            self.ax.set_facecolor(self._apply_appearance_mode(self._fg_color))
        except Exception:
            self.ax.set_facecolor(DARK_BG)

        remaining = self.target - self.current
        if self.monthly_saving > 0:
            months = math.ceil(remaining / self.monthly_saving)
        else:
            months = 24
        months = max(1, min(months, 60))

        x = range(0, months + 1)
        y = [min(self.target, self.current + i * self.monthly_saving) for i in x]

        self.ax.plot(x, y, color=self.color, linewidth=2)
        self.ax.fill_between(x, y, alpha=0.15, color=self.color)
        self.ax.axhline(self.target, color="#F59E0B", linewidth=1, linestyle="--", alpha=0.7)

        self.ax.set_xlabel("Miesięcy", fontsize=8)
        self.ax.set_ylabel("zł", fontsize=8)

        if months > 0:
            self.ax.annotate(f"{months} mies.", xy=(months, self.target),
                             xytext=(5, 5), textcoords="offset points",
                             fontsize=8, color=self.color)

        for spine_name in ["top", "right"]:
            self.ax.spines[spine_name].set_visible(False)
        self.fig.tight_layout(pad=0.3)

    def destroy(self):
        if hasattr(self, 'fig'):
            plt.close(self.fig)
        super().destroy()