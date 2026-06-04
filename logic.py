import calendar
from datetime import date, datetime, timedelta
from data_manager import (
    load_transactions,
    load_goals,
    load_settings,
    get_transactions_by_month,
    load_categories,
)


def format_currency(amount: float) -> str:
    """
    Formatuje kwotę w formacie polskim: 1234567.89 → "1 234 567,89 zł".
    Separator tysięcy: spacja. Dziesiętny: przecinek. Symbol na końcu.
    Ujemne: "-1 234,50 zł".
    """
    try:
        # Zaokrąglij do 2 miejsc po przecinku, aby uniknąć błędów zmiennoprzecinkowych
        rounded = round(amount, 2)
        if rounded < 0:
            sign = "-"
            rounded = -rounded
        else:
            sign = ""

        # Rozdziel na część całkowitą i ułamkową
        integer_part, _, frac_part = f"{rounded:.2f}".partition(".")

        # Grupowanie cyfr po 3 od prawej z użyciem spacji
        int_str = ""
        for i, ch in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                int_str = " " + int_str
            int_str = ch + int_str

        return f"{sign}{int_str},{frac_part} zł"
    except Exception:
        return "0,00 zł"


def get_monthly_summary(year: int, month: int) -> dict:
    """Zwraca podsumowanie miesięczne: przychody, wydatki, bilans oraz wydatki wg kategorii."""
    transactions = get_transactions_by_month(year, month)
    income = 0.0
    expense = 0.0
    category_totals = {}

    for t in transactions:
        amt = t.get("amount", 0.0)
        if t.get("type") == "income":
            income += amt
        elif t.get("type") == "expense":
            expense += amt
            cid = t.get("category_id")
            if cid is not None:
                category_totals[cid] = category_totals.get(cid, 0.0) + amt

    by_category = sorted(
        [{"category_id": k, "total": v} for k, v in category_totals.items()],
        key=lambda x: x["total"],
        reverse=True,
    )

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "by_category": by_category,
        "transaction_count": len(transactions),
    }


def get_today_budget() -> dict:
    """
    Oblicza budżet na dzisiejszy dzień.
    Uwzględnia miesięczny limit, dni miesiąca i dotychczasowe wydatki.
    """
    settings = load_settings()
    monthly_budget = settings.get("monthly_budget", 3000.0)
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    daily_budget = monthly_budget / days_in_month if days_in_month > 0 else 0.0

    transactions_month = get_transactions_by_month(today.year, today.month)
    transactions_today = [t for t in transactions_month if t["date"] == str(today) and t["type"] == "expense"]
    today_spent = sum(t["amount"] for t in transactions_today)

    month_expense = sum(t["amount"] for t in transactions_month if t["type"] == "expense")
    remaining_today = daily_budget - today_spent
    percent_of_daily = (today_spent / daily_budget * 100) if daily_budget > 0 else 0.0
    month_percent = (month_expense / monthly_budget * 100) if monthly_budget > 0 else 0.0

    if remaining_today >= daily_budget * 0.4:
        status = "ok"
    elif remaining_today >= 0:
        status = "warning"
    else:
        status = "danger"

    return {
        "daily_budget": daily_budget,
        "today_spent": today_spent,
        "remaining_today": remaining_today,
        "percent_of_daily": percent_of_daily,
        "month_expense": month_expense,
        "monthly_budget": monthly_budget,
        "month_percent": month_percent,
        "status": status,
    }


def forecast_month(year: int, month: int) -> dict:
    """
    Prognoza wydatków na koniec miesiąca na podstawie średnich dziennych wydatków.
    """
    today = date.today()
    days_in_month = calendar.monthrange(year, month)[1]

    # Dla bieżącego miesiąca bierzemy ile dni minęło, dla innych przyjmujemy cały miesiąc
    if today.year == year and today.month == month:
        current_day = today.day
    else:
        current_day = days_in_month  # cały miesiąc - brak danych dziennych

    transactions = get_transactions_by_month(year, month)
    spent = sum(t["amount"] for t in transactions if t["type"] == "expense")
    daily_avg = spent / current_day if current_day > 0 else 0.0
    forecast = daily_avg * days_in_month
    days_left = days_in_month - current_day

    settings = load_settings()
    monthly_budget = settings.get("monthly_budget", 3000.0)
    will_exceed = forecast > monthly_budget
    overshoot_by = max(0.0, forecast - monthly_budget)

    return {
        "spent_so_far": spent,
        "forecast_total": forecast,
        "daily_average": daily_avg,
        "days_left": days_left,
        "will_exceed": will_exceed,
        "overshoot_by": overshoot_by,
    }


def get_category_breakdown(year: int, month: int) -> list:
    """
    Grupuje wydatki wg kategorii i zwraca listę z nazwą, ikoną, kolorem,
    sumą i udziałem procentowym.
    """
    categories = {c["id"]: c for c in load_categories()}
    transactions = get_transactions_by_month(year, month)
    totals = {}

    for t in transactions:
        if t.get("type") == "expense":
            cid = t.get("category_id", 0)
            totals[cid] = totals.get(cid, 0.0) + t["amount"]

    total_expense = sum(totals.values())
    if total_expense == 0:
        total_expense = 1  # unikamy dzielenia przez zero

    breakdown = []
    for cid, total in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        cat = categories.get(cid, {"name": "Inne", "icon": "📦", "color": "#6B7280"})
        percent = round(total / total_expense * 100, 1)
        breakdown.append({
            "category_id": cid,
            "name": cat["name"],
            "icon": cat["icon"],
            "color": cat["color"],
            "total": total,
            "percent": percent,
        })

    return breakdown


def get_last_n_months_data(n: int = 6) -> list:
    """
    Zwraca listę podsumowań dla ostatnich n miesięcy (łącznie z bieżącym).
    """
    today = date.today()
    month_names = ["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze",
                   "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru"]
    result = []
    for i in range(n - 1, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        summary = get_monthly_summary(year, month)
        result.append({
            "label": month_names[month - 1],
            "year": year,
            "month": month,
            "income": summary["income"],
            "expense": summary["expense"],
            "balance": summary["balance"],
        })
    return result


def get_streak_days() -> int:
    """
    Zwraca liczbę kolejnych dni wstecz od dzisiaj, w których dodano
    co najmniej jedną transakcję (dowolnego typu).
    """
    transactions = load_transactions()
    dates_set = {t["date"] for t in transactions}
    streak = 0
    check_date = date.today()
    while str(check_date) in dates_set:
        streak += 1
        check_date -= timedelta(days=1)
    return streak


def get_biggest_expense_this_month() -> dict | None:
    """
    Znajduje największy wydatek bieżącego miesiąca i zwraca informacje o nim.
    """
    today = date.today()
    transactions = get_transactions_by_month(today.year, today.month)
    expenses = [t for t in transactions if t.get("type") == "expense"]
    if not expenses:
        return None

    biggest = max(expenses, key=lambda t: t["amount"])
    categories = {c["id"]: c for c in load_categories()}
    cat = categories.get(biggest.get("category_id", 0), {"name": "Inne", "icon": "📦"})

    return {
        "amount": biggest["amount"],
        "description": biggest.get("description", ""),
        "category_name": cat["name"],
        "category_icon": cat["icon"],
        "date": biggest["date"],
    }


def get_savings_rate(year: int, month: int) -> float:
    """
    Stopa oszczędności dla danego miesiąca: (dochód - wydatki) / dochód * 100%.
    """
    summary = get_monthly_summary(year, month)
    income = summary["income"]
    if income == 0:
        return 0.0
    return round((summary["balance"] / income) * 100, 1)


def animate_counter(label_widget, end_value: float, format_func=None, steps=25, duration_ms=700):
    """
    Animuje licznik na widgetach (np. CTkLabel) od 0 do end_value.
    label_widget.configure(text=...) aktualizuje wartość.
    format_func powinno przyjmować jedną liczbę i zwracać napis.
    """
    if format_func is None:
        format_func = str

    step_delay = max(1, duration_ms // steps)
    delta = end_value / steps if steps > 0 else 0.0

    def _step(step, current):
        if step >= steps:
            label_widget.configure(text=format_func(end_value))
            return
        label_widget.configure(text=format_func(current))
        label_widget.after(step_delay, lambda: _step(step + 1, current + delta))

    _step(0, 0.0)