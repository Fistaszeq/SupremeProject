# Uruchamiaj TYLKO ten plik: python main.py

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from gui import customtkinter as ctk
from data_manager import init_data, load_settings
from panels import PanelManager

# Inicjalizacja danych i ustawień
init_data()
settings = load_settings()

# Konfiguracja wyglądu
ctk.set_appearance_mode(settings.get("theme", "dark"))
ctk.set_default_color_theme("blue")

# Import GUI – plik gui.py w tym samym katalogu
import gui.gui as gui

# Przygotowanie słownika z ramkami (tworzonymi w gui.py)
frames = {
    "left_top":     gui.section_left_top,
    "right_top":    gui.section_right_top,
    "left_bottom":  gui.section_left_bottom,
    "right_bottom": gui.section_right_bottom,
    "bottom":       gui.section_bottom,
    "right":        gui.section_right,
}

# Inicjalizacja menadżera paneli
manager = PanelManager(frames)

# Podpięcie komend do przycisków nawigacyjnych
gui.desktop_btn.configure(command=manager.show_dashboard)
gui.transactions_btn.configure(command=manager.show_transactions)
gui.categories_btn.configure(command=manager.show_categories)
gui.goals_btn.configure(command=manager.show_goals)
gui.raports_btn.configure(command=manager.show_reports)
gui.settings_btn.configure(command=manager.show_settings)

# Rejestracja przycisków w menadżerze (do podświetlania aktywnego)
nav_buttons = {
    "dashboard":    gui.desktop_btn,
    "transactions": gui.transactions_btn,
    "categories":   gui.categories_btn,
    "goals":        gui.goals_btn,
    "reports":      gui.raports_btn,
    "settings":     gui.settings_btn,
}
manager.register_nav_buttons(nav_buttons)

# Wyświetlenie daty w górnym pasku
from datetime import date
ctk.CTkLabel(
    gui.section_top,
    text=f"💰 BudżetApp  •  {date.today().strftime('%d.%m.%Y')}",
    font=ctk.CTkFont("Segoe UI", 14)
).place(x=20, y=22)

# Uruchomienie pętli głównej aplikacji
gui.app.mainloop()