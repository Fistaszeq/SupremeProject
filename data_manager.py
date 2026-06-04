import json
import os
from datetime import date

# Stałe ścieżek
DATA_DIR = "data"
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
GOALS_FILE = os.path.join(DATA_DIR, "goals.json")


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
        {"id": 6, "name": "Wynagrodzenie", "color": "#10B981", "icon": "💼", "type": "income"},
        {"id": 7, "name": "Freelance", "color": "#3B82F6", "icon": "💻", "type": "income"},
        {"id": 8, "name": "Inne", "color": "#6B7280", "icon": "📦", "type": "both"}
    ]

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


def load_transactions():
    """Wczytuje i zwraca listę transakcji z pliku JSON."""
    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_transactions(transactions):
    """Zapisuje listę transakcji do pliku JSON."""
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)


def add_transaction(amount, type, category_id, description, date_str):
    """
    Dodaje nową transakcję do listy i zapisuje.
    Zwraca utworzoną transakcję jako słownik.
    """
    transactions = load_transactions()
    new_id = max((t["id"] for t in transactions), default=0) + 1
    transaction = {
        "id": new_id,
        "amount": float(amount),
        "type": type,
        "category_id": int(category_id),
        "description": description,
        "date": date_str
    }
    transactions.append(transaction)
    save_transactions(transactions)
    return transaction


def delete_transaction(transaction_id):
    """
    Usuwa transakcję o podanym id.
    Zwraca True jeśli znaleziono i usunięto, w przeciwnym razie False.
    """
    transactions = load_transactions()
    for i, t in enumerate(transactions):
        if t["id"] == transaction_id:
            del transactions[i]
            save_transactions(transactions)
            return True
    return False


def load_categories():
    """Wczytuje i zwraca listę kategorii."""
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_goals():
    """Wczytuje i zwraca listę celów oszczędnościowych."""
    with open(GOALS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_goals(goals):
    """Zapisuje listę celów do pliku JSON."""
    with open(GOALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(goals, f, indent=2, ensure_ascii=False)


def get_transactions_by_month(year, month):
    """
    Filtruje transakcje po podanym roku i miesiącu.
    Format daty w pliku: "YYYY-MM-DD".
    """
    transactions = load_transactions()
    result = []
    for t in transactions:
        # Zakładamy, że data zawsze w formacie YYYY-MM-DD
        try:
            d = date.fromisoformat(t["date"])
            if d.year == year and d.month == month:
                result.append(t)
        except (ValueError, KeyError):
            # Jeśli data jest nieprawidłowa, pomijamy transakcję
            continue
    return result


if __name__ == "__main__":
    init_data()
    print("Data manager OK")
    print(f"Kategorie: {len(load_categories())}")