# Progress

## Day 1 - 03.10.2026

## Problem Odbiorcy

Zdefiniowaliśmy odbiorców: Docelowym odbiorcą naszego rozwiązania są zarówno prywatni inwestorzy,
jak i również firmy zajmujące się rafinerią i przetwarzaniem wyrobów ze złota.

## Wybór tematu

Przedmiotem naszego rozwiązania jest analiza i predykcja cen złota na podstawie determinant ściśle związanych
z gospodarką, kursów walut oraz innych zmiennych, które uznaliśmy za istotne w kontekście badanego problemu.

## Zmienne objaśniane i objaśniające

Zmienną objaśnianą jest cena za 1 gram złota próby 1000 wyrażona w PLN, publikowana przez Narodowy Bank Polski.
Docelowo nasz produkt ma analizować cenę dla kolejnego dnia publikacji notowania.

Wybrane na ten moment zmienne objaśniające:

1. Historyczne ceny złota - NBP.
2. Kurs USD/PLN - NBP.
3. Kurs EUR/PLN - NBP.
4. Kurs CHF/PLN - NBP.
5. Rentowność 10-letnich obligacji skarbowych USA - FRED, DGS10.
6. Rentowność 2-letnich obligacji skarbowych USA - FRED, DGS2.
7. Realna rentowność 10-letnich obligacji skarbowych USA
   indeksowanych inflacją - FRED, DFII10.
8. Efektywna stopa funduszy federalnych - FRED, DFF.
9. Miara oczekiwań inflacyjnych na okres 10 lat, wyznaczana
   jako różnica rentowności obligacji nominalnych i indeksowanych
   inflacją - FRED, T10YIE.
10. Indeks zmienności rynku akcji VIX - FRED, VIXCLS.
11. Cena ropy naftowej WTI - FRED, DCOILWTICO.
12. Indeks giełdowy NASDAQ Composite - FRED, NASDAQCOM.
13. Indeks cen konsumpcyjnych w USA - FRED, CPIAUCSL.
14. Stopa bezrobocia w USA - FRED, UNRATE.

Na podstawie powyższych danych planujemy również wyznaczyć zmienne pochodne, tzn. opóźnione wartości zmiennej objaśnianej, zmiany procentowe, średnie kroczące itd.

Lista powyższych zmiennych jest jedynie początkowym zestawem kandydatów. Przydatność poszczególnych zmiennych zostanie oceniona podczas analizy i porównania wyników modeli.

Źródła danych:
-NBP: <https://api.nbp.pl/>
-FRED: <https://fred.stlouisfed.org/>

## Day 2 - 04.10.2026

## Dokumentacja projektu

Rozbudowaliśmy README o cel projektu, potrzeby odbiorców,
pytania analityczne oraz planowany sposób pozyskiwania
i przetwarzania danych. Określiliśmy również sposób oceny
przyszłych modeli prognostycznych.

## Pobieranie danych z NBP

Rozszerzyliśmy zakres pobierania cen złota do ostatnich 10 lat.
Ze względu na limit API podzieliliśmy ten okres na przedziały
obejmujące maksymalnie 93 dni. Wyniki kolejnych zapytań
łączymy w jedną listę uporządkowaną według daty.

Dodaliśmy pobieranie kursów średnich USD/PLN, EUR/PLN
i CHF/PLN z tabeli A NBP dla tego samego okresu.

Przygotowaliśmy funkcję `fetch_all()`, która wywołuje pobieranie
złota i walut. Podłączyliśmy ją do przycisku w dashboardzie.

## Konfiguracja aplikacji

Przenieśliśmy klucz Django i klucz API FRED do lokalnego
pliku `.env`. W ustawieniach aplikacji dodaliśmy ich odczyt
przy użyciu biblioteki `python-dotenv`.

## Day 3 - 5.10.2026

## Integracja danych z FRED

Podłączyliśmy do wspólnego pobierania wszystkie wybrane serie FRED.
Rozszerzyliśmy zakres pobierania danych do ostatnich 13 lat.

## Przechowywanie danych

Dodaliśmy zapis rekordów do pliku JSON, w katalogu `data/raw`.
Każde pobranie jest parą `value-date`.

Rozdzieliliśmy przechowywanie na warstwy `raw`, `clean`, `serving` w katalogu `django/data`.

## Czyszczenie danych

Przygotowaliśmy funkcje: `clean_series()` oraz `clean_all()`, wykorzystując pandas i numpy.
Ujednoliciliśmy nazwy kolumn, przekonwertowaliśmy daty i wartości liczbowe
oraz uporządkowaliśmy rekordy wg. daty (wraz z indeksami).

Dodaliśmy kontrole wymaganych pól, brakujących i powtarzających
się dat, wartości nieskończonych oraz dodatnich cen złota
i kursów walut. Liczba rekordów i braków jest wypisywana
w terminalu.

Oczyszczone serie zapisujemy jako csv w `clean`.

## Łączenie danych

Dodaliśmy funkcje `merge_series()`, która łączy oczyszczone serie po dacie.
Sprawdzana jest unikalność dat podczas łaćzenia oraz zachowanie liczby notowań złota.
Wynik tego działania zapisujemy jako wspólny plik CSV w warstwie `serving`.

## Day 4 - 7.10.2026

Dodaliśmy funkcję, która usuwa wiersze w których występują NaN bądź puste wartości.
Przez problemy z integracją z całością zbioru danych zdecydowaliśmy się na usunięcie dwóch zmiennych: "CPIAUCSL", "UNRATE".

## Day 5 - 13.10.2026

### Cechy czasowe

Dodaliśmy funkcję `add_time_features()` w data_processing/time_features.py.
Wyznaczamy opóźnione ceny złota `gold_lag_1`, `gold_lag_7`
i `gold_lag_14` oraz procentową zmianę ceny `gold_change_pct`.
Opóźnienia dotyczą kolejnych notowań, a nie dni kalendarzowych.
Cechy powstają po połączeniu serii, przed usunięciem wierszy
z brakującymi wartościami i zapisaniem danych do serving.

### Przygotowanie danych do modelowania

Utworzyliśmy moduł `model_processing/create_model.py`, który zawiera
funkcje przygotowania danych, uczenia modelu i oceny prognoz.

Funkcja `prepare_model_data()` porządkuje dane chronologicznie,
sprawdza wymagane kolumny, brakujące daty, typy liczbowe
oraz brak wartości NaN i nieskończonych.
Powtarzające się daty są obecnie wypisywane w terminalu,
ale nie przerywają przygotowania danych.

Tworzymy pary: cechy bieżącego notowania jako *`X`* oraz cena złota
z następnego zachowanego wiersza jako *`y`*. Aktualna cena złota
pozostaje również cechą wejściową.

Dane dzielimy chronologicznie na trening, walidację i test
w proporcjach 70/20/10. `StandardScaler` dopasowujemy wyłącznie
do treningu, a walidację i test przekształcamy tymi samymi
parametrami, obliczonymi osobno dla każdej kolumny.

### Model i przeszukiwanie hiperparametrów

Dodaliśmy uczenie sieci MLPRegressor z aktywacją ReLU,
optymalizatorem Adam i ustalonym random_state=42.

Przy użyciu ParameterGrid przygotowaliśmy przeszukiwanie
48 konfiguracji obejmujących:

- architektury: (32, 16), (64, 32), (128, 64) i (8, 4, 2);
- regularyzację alpha: 0.001 i 0.01;
- początkowe tempo uczenia: 0.0005 i 0.001;
- rozmiar partii: auto, 18 i 32.

Każda konfiguracja uczy się wyłącznie na treningu. Wybieramy
model z najniższym `MAE` na naszym chronologicznym zbiorze walidacyjnym.
Ranking konfiguracji, błędy oraz liczby wykonanych epok
są wypisywane w terminalu.

Dodaliśmy opcjonalną standaryzację zmiennej objaśnianej przez
`TransformedTargetRegressor`, z automatycznym odwracaniem transformacji
prognoz. Obecne wywołanie w widoku pozostawia tę opcję wyłączoną.

### Ocena i integracja z aplikacją

Dodaliśmy obliczanie `MAE`, `RMSE` i `R²`.
Podłączyliśmy akcję create_model do przycisku w aplikacji.
Widok wczytuje najnowszy plik `*_merged.csv` z *`serving`*,
uruchamia przygotowanie danych i uczenie, a następnie wypisuje
miary modelu w terminalu.

Aktualnie najlepsza konfiguracja to:
{'alpha': 0.01, 'batch_size': 32, 'hidden_layer_sizes': (8, 4, 2), 'learning_rate_init': 0.001}
Z miarami wynoszącymi: *`"MAE": 3.3452`*; *`"RMSE": 4.39`*; *`'R2': 0.991`*.
