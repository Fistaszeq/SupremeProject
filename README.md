# 💸 BudgetFlow – Dokumentacja Projektowa

BudgetFlow to zaawansowana aplikacja do zarządzania finansami osobistymi, zaprojektowana z myślą o przejrzystości, estetyce (styl iOS Dark Mode) i bezpieczeństwie danych.

## 🎤 Skrypt na Prezentację

### 1. Ogół działania aplikacji
"Aplikacja pełni rolę osobistego centrum finansów. Główne okno jest podzielone na dwie strefy: lewą – zarządzanie kontami (podgląd stanu, edycja, tworzenie) oraz prawą – historię operacji i szybkie akcje."

### 2. Funkcjonalności (Co pokazujemy?)
* **Konta:** Możemy tworzyć wiele kont (np. Portfel, Bank) z przypisanymi kolorami.
* **Operacje:** Szybkie dodawanie wpłat i wypłat. 
    * *Tip:* W oknie dodawania działa klawisz **Enter**, który natychmiast zatwierdza operację.
* **Historia:** Po prawej stronie widać listę transakcji. Jeśli często robimy te same wydatki, opcja **"Ponów"** kopiuje dane wpisu, oszczędzając czas.
* **Szczegóły:** Klikając w konto, przechodzimy do szczegółowego widoku z wykresem kołowym wydatków.
* **Statystyki:** Osobna zakładka, gdzie agregujemy dane z całego budżetu.

### 3. Aspekty techniczne (UX & Bezpieczeństwo)
* **Responsive Design:** Aplikację można dowolnie resizować; przy większej liczbie danych pojawia się przewijanie (scroll).
* **Bezpieczeństwo:** Każde usunięcie konta wymaga potwierdzenia. Zaimplementowano usuwanie kaskadowe (`ON DELETE CASCADE`) – usuwając konto, czyścimy powiązane wpisy, by nie zostawiać "śmieci" w bazie.
* **Walidacja:** System informuje o błędnych danych i komunikatami kieruje użytkownika, gdy np. próbuje dodać wpis bez utworzonego wcześniej konta.
* **Performance:** Przy przełączaniu między widokami dodaliśmy "ładowanie danych", co daje użytkownikowi sygnał, że aplikacja pracuje.
* **Multi-platform:** Projekt działa na Windowsie i Linuxie.

### 4. Architektura plików
* `run_budget.py`: Główny punkt wejścia.
* `budget_app.py`: "Serce" GUI – kafelki, zakładki, mechanika układu.
* `budget_dialogs.py`: Wszystkie okna popup (formularze).
* `budget_db.py`: Logika SQL – bezpieczne zapytania, schematy bazy SQLite.

---

## 🛠️ Plan rozwoju (Roadmap)
W przyszłości planujemy:
* **Własne kategorie:** Możliwość definiowania własnych tagów.
* **Dopracowanie UX:** Lepsza kontrola nad przestrzenią przy resizowaniu okna.
* **Dopamina:** Dodanie płynnych animacji przy wczytywaniu danych.
* **Walidacja:** Blokada duplikatów nazw kont.
* **Fix:** Naprawa buga ze statystykami (obecnie po usunięciu konta statystyki wymagają odświeżenia/poprawy).

---

## 👥 Zespół
* **Fistaszeq** – Main Programmer
* **Alana** – QA & Data Analyst
* **Maja** – UI/UX Designer
* **Tomek** – Implementacja funkcji

*Projekt stworzony w celach edukacyjnych, zoptymalizowany pod kątem stabilności i łatwej konserwacji kodu.*
