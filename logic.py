import calendar
from datetime import date
from data_manager import load_transactions, load_goals, get_transactions_by_month, load_categories


def get_monthly_summary(year: int, month: int) -> dict:
    """
    Oblicza podsumowanie miesięczne: przychody, wydatki, bilans
    oraz wydatki pogrupowane według kategorii (posortowane malejąco).
    """
    try:
        transactions = get_transactions_by_month(year, month)
    except Exception as e:
        print(f"Błąd pobierania transakcji dla {year}-{month:02d}: {e}")
        return {"income": 0.0, "expense": 0.0, "balance": 0.0, "by_category": []}

    income = 0.0
    expense = 0.0
    category_totals = {}

    for t in transactions:
        if t["type"] == "income":
            income += t["amount"]
        elif t["type"] == "expense":
            expense += t["amount"]
            cat_id = t["category_id"]
            category_totals[cat_id] = category_totals.get(cat_id, 0.0) + t["amount"]

    # Przekształć słownik na listę i posortuj malejąco po sumie
    by_category = [
        {"category_id": cat_id, "total": total}
        for cat_id, total in category_totals.items()
    ]
    by_category.sort(key=lambda x: x["total"], reverse=True)

    balance = income - expense

    return {
        "income": income,
        "expense": expense,
        "balance": balance,
        "by_category": by_category
    }


def get_today_budget(monthly_budget: float, year: int, month: int) -> dict:
    """
    Oblicza, ile można dziś wydać na podstawie miesięcznego budżetu.
    Zwraca słownik z kluczami: daily_budget, today_spent, remaining_today, status.
    """
    try:
        # Liczba dni w danym miesiącu
        days_in_month = calendar.monthrange(year, month)[1]
        daily_budget = monthly_budget / days_in_month if days_in_month > 0 else 0.0

        # Pobranie dzisiejszej daty
        today = date.today()
        today_spent = 0.0

        # Jeśli podany miesiąc jest bieżącym, policz dzisiejsze wydatki
        if year == today.year and month == today.month:
            transactions = get_transactions_by_month(year, month)
            for t in transactions:
                if t["type"] == "expense" and t["date"] == today.isoformat():
                    today_spent += t["amount"]
        else:
            # Jeśli miesiąc nie jest bieżący, today_spent wynosi 0
            pass

        remaining_today = daily_budget - today_spent
        status = "ok" if remaining_today >= 0 else "over"

        return {
            "daily_budget": daily_budget,
            "today_spent": today_spent,
            "remaining_today": remaining_today,
            "status": status
        }
    except Exception as e:
        print(f"Błąd w get_today_budget: {e}")
        return {
            "daily_budget": 0.0,
            "today_spent": 0.0,
            "remaining_today": 0.0,
            "status": "ok"
        }


def forecast_month(year: int, month: int) -> dict:
    """
    Prognozuje całkowite wydatki na koniec miesiąca na podstawie
    średnich dziennych wydatków do dnia dzisiejszego.
    """
    try:
        today = date.today()
        # Prognoza ma sens tylko dla bieżącego miesiąca
        if year != today.year or month != today.month:
            # Dla innych miesięcy zwracamy domyślne wartości
            return {
                "spent_so_far": 0.0,
                "forecast_total": 0.0,
                "daily_average": 0.0,
                "days_left": 0
            }

        transactions = get_transactions_by_month(year, month)
        spent_so_far = 0.0

        # Suma wydatków do dnia dzisiejszego (włącznie)
        for t in transactions:
            if t["type"] == "expense":
                trans_date = date.fromisoformat(t["date"])
                if trans_date <= today:
                    spent_so_far += t["amount"]

        day_of_month = today.day
        days_in_month = calendar.monthrange(year, month)[1]
        days_left = days_in_month - day_of_month

        # Średnia dzienna na podstawie dotychczasowych dni
        if day_of_month > 0:
            daily_average = spent_so_far / day_of_month
        else:
            daily_average = 0.0

        forecast_total = daily_average * days_in_month

        return {
            "spent_so_far": spent_so_far,
            "forecast_total": forecast_total,
            "daily_average": daily_average,
            "days_left": days_left
        }
    except Exception as e:
        print(f"Błąd w forecast_month: {e}")
        return {
            "spent_so_far": 0.0,
            "forecast_total": 0.0,
            "daily_average": 0.0,
            "days_left": 0
        }


def get_savings_progress(goal_id: int) -> dict | None:
    """
    Oblicza postęp realizacji celu oszczędnościowego o podanym id.
    Zwraca słownik z danymi celu lub None, jeśli cel nie istnieje.
    """
    try:
        goals = load_goals()
        for goal in goals:
            if goal["id"] == goal_id:
                target = goal.get("target", 0.0)
                current = goal.get("current", 0.0)
                percent = (current / target * 100.0) if target > 0 else 0.0
                remaining = target - current
                return {
                    "name": goal.get("name", ""),
                    "target": target,
                    "current": current,
                    "percent": percent,
                    "remaining": remaining
                }
        return None
    except Exception as e:
        print(f"Błąd w get_savings_progress: {e}")
        return None


def get_category_breakdown(year: int, month: int) -> list:
    """
    Grupuje wydatki wg kategorii, uzupełnia o nazwy, ikony i kolory,
    oblicza udział procentowy. Wynik posortowany malejąco po kwocie.
    """
    try:
        transactions = get_transactions_by_month(year, month)
    except Exception as e:
        print(f"Błąd pobierania transakcji: {e}")
        return []

    # Zbierz wydatki wg category_id
    expense_by_cat = {}
    total_expenses = 0.0
    for t in transactions:
        if t["type"] == "expense":
            cat_id = t["category_id"]
            expense_by_cat[cat_id] = expense_by_cat.get(cat_id, 0.0) + t["amount"]
            total_expenses += t["amount"]

    # Wczytaj kategorie
    try:
        categories = load_categories()
    except Exception as e:
        print(f"Błąd ładowania kategorii: {e}")
        return []

    # Zbuduj słownik kategorii po id dla szybkiego dostępu
    cat_dict = {c["id"]: c for c in categories}

    breakdown = []
    for cat_id, total in expense_by_cat.items():
        cat_info = cat_dict.get(cat_id, {})
        percent = (total / total_expenses * 100.0) if total_expenses > 0 else 0.0
        breakdown.append({
            "name": cat_info.get("name", f"Kat.{cat_id}"),
            "icon": cat_info.get("icon", ""),
            "color": cat_info.get("color", "#888888"),
            "total": total,
            "percent": percent
        })

    # Sortuj malejąco
    breakdown.sort(key=lambda x: x["total"], reverse=True)
    return breakdown


def format_currency(amount: float) -> str:
    """
    Formatuje kwotę do postaci: 1 234,50 zł.
    """
    try:
        # Formatowanie z dwoma miejscami po przecinku, przecinek jako separator dziesiętny
        formatted = f"{amount:,.2f}"
        # Zamień przecinki na spacje, kropkę na przecinek
        formatted = formatted.replace(",", " ").replace(".", ",")
        return f"{formatted} zł"
    except Exception as e:
        print(f"Błąd formatowania kwoty: {e}")
        return "0,00 zł"