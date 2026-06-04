import json
import os
from datetime import date

# Stałe ścieżek
DATA_DIR = "data"
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
GOALS_FILE = os.path.join(DATA_DIR, "goals.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


def init_data():
    """Tworzy folder data i domyślne pliki JSON, jeśli nie istnieją."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Domyślne kategorie
    default_categories = [
        {"id": 1, "name": "Jedzenie", "color": "#EF4444", "icon": "🍔", "type": "expense"},
        {"id": 2, "name": "Transport", "color": "#F59E0B", "icon": "🚗", "type": "expense"},
        {"id": 3, "name": "Mieszkanie", "color": "#8B5CF6", "icon": "🏠", "type": "expense"},
        {"id": 4, "name": "Rozrywka", "color": "#EC4899", "icon": "🎮", "type": "expense"},
        {"id": 5, "name": "Zdrowie", "color": "#06B6D4", "icon": "💊", "type": "expense"},
        {"id": 6, "name": "Ubrania", "color": "#84CC16", "icon": "👗", "type": "expense"},
        {"id": 7, "name": "Wynagrodzenie", "color": "#10B981", "icon": "💼", "type": "income"},
        {"id": 8, "name": "Freelance", "color": "#3B82F6", "icon": "💻", "type": "income"},
        {"id": 9, "name": "Oszczędności", "color": "#F59E0B", "icon": "🏦", "type": "expense"},
        {"id": 10, "name": "Inne", "color": "#6B7280", "icon": "📦", "type": "both"},
    ]

    # Domyślne ustawienia
    default_settings = {"monthly_budget": 3000.0, "theme": "dark", "currency": "zł"}

    # Plik transakcji
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)

    # Plik kategorii
    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_categories, f, indent=2, ensure_ascii=False)

    # Plik celów
    if not os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)

    # Plik ustawień
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2, ensure_ascii=False)


def load_transactions() -> list:
    """Wczytuje i zwraca listę transakcji z pliku JSON."""
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_transactions(transactions: list):
    """Zapisuje listę transakcji do pliku JSON."""
    try:
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu transakcji: {e}")


def add_transaction(amount, type, category_id, description, date_str) -> dict:
    """
    Dodaje nową transakcję do listy i zapisuje.
    Zwraca utworzoną transakcję jako słownik.
    """
    try:
        transactions = load_transactions()
        new_id = max((t["id"] for t in transactions), default=0) + 1
        transaction = {
            "id": new_id,
            "amount": float(amount),
            "type": type,
            "category_id": int(category_id),
            "description": description,
            "date": date_str,
        }
        transactions.append(transaction)
        save_transactions(transactions)
        return transaction
    except Exception as e:
        print(f"Błąd dodawania transakcji: {e}")
        return {}


def delete_transaction(transaction_id: int) -> bool:
    """
    Usuwa transakcję o podanym id.
    Zwraca True jeśli znaleziono i usunięto.
    """
    try:
        transactions = load_transactions()
        for i, t in enumerate(transactions):
            if t["id"] == transaction_id:
                del transactions[i]
                save_transactions(transactions)
                return True
        return False
    except Exception as e:
        print(f"Błąd usuwania transakcji: {e}")
        return False


def load_categories() -> list:
    """Wczytuje i zwraca listę kategorii."""
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def load_goals() -> list:
    """Wczytuje i zwraca listę celów oszczędnościowych."""
    try:
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_goals(goals: list):
    """Zapisuje listę celów do pliku JSON."""
    try:
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(goals, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu celów: {e}")


def add_goal(name: str, target_amount: float, color: str = "#3B82F6") -> dict:
    """
    Dodaje nowy cel oszczędnościowy.
    Zwraca utworzony cel jako słownik.
    """
    try:
        goals = load_goals()
        new_id = max((g["id"] for g in goals), default=0) + 1
        goal = {
            "id": new_id,
            "name": name,
            "target_amount": float(target_amount),
            "current_amount": 0.0,
            "color": color,
            "created_date": str(date.today()),
        }
        goals.append(goal)
        save_goals(goals)
        return goal
    except Exception as e:
        print(f"Błąd dodawania celu: {e}")
        return {}


def add_deposit_to_goal(goal_id: int, amount: float) -> bool:
    """
    Dodaje wpłatę do celu oszczędnościowego.
    current_amount nie przekroczy target_amount.
    Zwraca True jeśli znaleziono cel.
    """
    try:
        goals = load_goals()
        for goal in goals:
            if goal["id"] == goal_id:
                new_current = goal.get("current_amount", 0.0) + float(amount)
                target = goal.get("target_amount", 0.0)
                goal["current_amount"] = min(new_current, target)
                save_goals(goals)
                return True
        return False
    except Exception as e:
        print(f"Błąd wpłaty na cel: {e}")
        return False


def get_transactions_by_month(year: int, month: int) -> list:
    """
    Filtruje transakcje po roku i miesiącu.
    Data w formacie "YYYY-MM-DD".
    """
    try:
        prefix = f"{year}-{month:02d}"
        transactions = load_transactions()
        return [t for t in transactions if t.get("date", "").startswith(prefix)]
    except Exception:
        return []


def load_settings() -> dict:
    """Wczytuje i zwraca ustawienia. Przy błędzie zwraca domyślne."""
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"monthly_budget": 3000.0, "theme": "dark", "currency": "zł"}


def save_settings(settings: dict):
    """Zapisuje ustawienia do pliku JSON."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu ustawień: {e}")


def update_setting(key: str, value) -> bool:
    """
    Aktualizuje pojedyncze ustawienie.
    Zwraca True po pomyślnym zapisie.
    """
    try:
        settings = load_settings()
        settings[key] = value
        save_settings(settings)
        return True
    except Exception as e:
        print(f"Błąd aktualizacji ustawienia '{key}': {e}")
        return False


if __name__ == "__main__":
    init_data()
    print("OK:", load_settings())