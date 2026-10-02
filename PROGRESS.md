# Day 1

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
