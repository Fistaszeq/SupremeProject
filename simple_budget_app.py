"""
Plik startowy aplikacji.
"""

from budget_app import SimpleBudgetApp


if __name__ == "__main__":
    app = SimpleBudgetApp()
    app.mainloop()
    app.db.close()
