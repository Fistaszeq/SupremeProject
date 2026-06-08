"""
Plik startowy aplikacji.

Edytorzy:
- nie modyfikuj tu logiki, tylko uruchamiaj moduł główny z budget_app.py,
- jeśli chcesz zmienić UI lub dane, edytuj odpowiedni moduł.
"""

from budget_app import SimpleBudgetApp


if __name__ == "__main__":
    app = SimpleBudgetApp()
    app.mainloop()
    app.db.close()
