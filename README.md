# 💸 BudgetFlow
*Profesjonalna aplikacja do zarządzania budżetem domowym.*

## 📋 Opis projektu
**BudgetFlow** to desktopowa aplikacja finansowa, stworzona z myślą o użytkownikach ceniących estetykę i wydajność. Projekt skupia się na pełnym cyklu życia danych finansowych – od rejestracji kont, przez księgowanie transakcji, aż po zaawansowaną analitykę wydatków.

## 🛠 Technologie i Architektura
Projekt został zrealizowany w oparciu o nowoczesny stos technologiczny zapewniający stabilność i skalowalność:

* **Język:** Python 3.8+
* **Interfejs GUI:** `customtkinter` (nowoczesne widżety z natywnym wsparciem dla Dark Mode) oraz `tkinter`.
* **Baza Danych:** `sqlite3` – relacyjna baza danych z wymuszoną integralnością referencyjną (`PRAGMA foreign_keys = ON`).
* **Analityka:** `matplotlib` (obiektowy interfejs `Figure`) do generowania dynamicznych wykresów analitycznych.

## 🏗 Architektura systemu
Aplikacja wykorzystuje architekturę warstwową (zbliżoną do MVC), co zapewnia separację logiki od interfejsu:
* **Warstwa Modelu (`budget_db.py`):** Odpowiada za bezpośrednią komunikację z bazą SQLite, bezpieczne transakcje (ACID) oraz operacje na danych.
* **Warstwa Kontrolera (`budget_app.py`):** Zarządza stanem aplikacji, obsługuje zdarzenia (events) i steruje przepływem danych między bazą a widokami.
* **Warstwa Widoku (`budget_dialogs.py`):** Odpowiada za responsywne okna dialogowe i formularze w stylu iOS Design.

## ✨ Kluczowe funkcjonalności

### 1. Zarządzanie portfelem (CRUD)
* **Konta:** Tworzenie wielu rachunków z przypisanymi kolorami identyfikacyjnymi.
* **Edycja i usuwanie:** Pełna kontrola nad danymi. Dzięki relacjom w bazie (`ON DELETE CASCADE`), usunięcie konta czyści również przypisane do niego transakcje, dbając o porządek w bazie.

### 2. Księgowanie i analiza
* **Rejestr transakcji:** Wpłaty i wypłaty z obsługą notatek, kategorii (tagów) oraz datowania wpisów.
* **Funkcja „Ponów”:** Szybkie powielanie historycznych transakcji (autofill), skracające czas wprowadzania powtarzalnych kosztów.
* **Analityka:** Okno szczegółów konta z wykresami pierścieniowymi (Donut Chart) oraz zakładka z globalnymi statystykami tagów.

### 3. Optymalizacja i UX
* **Tryb Ciemny (iOS Design):** Spójna paleta kolorów i nowoczesne komponenty (Segmented Buttons, ComboBoxes).
* **Responsywność:** Aplikacja obsługuje zmianę rozmiaru okna, automatycznie skalując elementy interfejsu.
* **Wydajność:** Asynchroniczne odświeżanie widoków (loading screen) oraz buforowanie komponentów (View Caching) eliminują opóźnienia przy przełączaniu zakładek.

## 🚀 Instrukcja uruchomienia
1. Instalacja zależności:
   ```bash
   pip install customtkinter matplotlib
   ```
2. Uruchomienie
   ```bash
   python budget_app.py
   ```
   

