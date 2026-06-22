"""
Lekki launcher aplikacji budżetowej.

Uruchom:
    python3 run_budget.py
"""

from budget_app import SimpleBudgetApp


if __name__ == "__main__":
    app = SimpleBudgetApp()
    try:
        app.mainloop()
    finally:
        app.db.close()
