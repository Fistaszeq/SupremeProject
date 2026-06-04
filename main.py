# Uruchamiaj TYLKO ten plik: python main.py

import customtkinter as ctk
from data_manager import init_data
from panels import PanelManager

# ── Inicjalizacja danych ────────────────────────────────────
init_data()

# ── CustomTkinter setup ─────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Import komponentów GUI (tworzonych przez Maję) ──────────
# UWAGA: importujemy zmienne z gui.py, NIE odpala mainloop
import gui.gui as gui  # to wykona kod w gui.py i stworzy okno

# ── Panel Manager ───────────────────────────────────────────
frames = {
    "left_top":     gui.section_left_top,
    "right_top":    gui.section_right_top,
    "left_bottom":  gui.section_left_bottom,
    "right_bottom": gui.section_right_bottom,
    "bottom":       gui.section_bottom,
    "right":        gui.section_right,
}

manager = PanelManager(frames)

# ── Podpinanie przycisków nawigacyjnych ─────────────────────
nav_buttons = {
    "dashboard":    gui.desktop_btn,
    "transactions": gui.transactions_btn,
    "categories":   gui.categories_btn,
    "goals":        gui.goals_btn,
    "reports":      gui.raports_btn,
    "settings":     gui.settings_btn,
}

gui.desktop_btn.configure(command=manager.show_dashboard)
gui.transactions_btn.configure(command=manager.show_transactions)
gui.categories_btn.configure(command=manager.show_categories)
gui.goals_btn.configure(command=manager.show_goals)
gui.raports_btn.configure(command=manager.show_reports)
gui.settings_btn.configure(command=manager.show_settings)

manager.register_nav_buttons(nav_buttons)

# ── Topbar info ─────────────────────────────────────────────
from datetime import date
today_label = ctk.CTkLabel(
    gui.section_top,
    text=f"Budżet Domowy  •  {date.today().strftime('%d.%m.%Y')}",
    font=ctk.CTkFont(family="Segoe UI", size=14)
)
today_label.place(x=20, y=20)

# ── Start aplikacji ─────────────────────────────────────────
gui.app.mainloop()