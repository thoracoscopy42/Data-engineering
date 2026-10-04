# Golden Predictor

Projekt jest realizowany w ramach przedmiotu *Inżynieria Danych*.
Obejmuje on budowę data pipeline-u oraz aplikacji internetowej służącej za dashboard.
Docelowa funkcjonalność to analiza historycznych cen złota i prognozowanie jego ceny na koleny dzień publikacji notowań.

## 1. Cel, odbiorcy i problem projektu

Celem projektu jest przygotowanie powtarzalnego procesu automatycznego pozyskania i procesowania danych dotyczących cen złota
oraz wybranych wskaźników makroekonomicznych i rynkowych.

Docelowymi odbiorcami rozwiązania są prywatni inwestorzy
oraz osoby odpowiedzialne za zakupy surowca w przedsiębiorstwach
zajmujących się rafinacją złota i produkcją wyrobów ze złota.

Potrzebą odbiorców jest uzyskanie historii cen, informacji o zmianach rynku oraz prognozy. Aplikacja ma być automatyzacją procesów ręcznego pobierania i zestawiania danych oraz wspierać monitorowanie rynku przed decyzją zakupową.

Zakres projektu obejmuje publikowaną przez NBP cenę 1 grama złota próby 1000, wyrażoną w PLN.

### Pytania analityczne

1. Jak zmieniała się cena złota w PLN w wybranym okresie?

2. W jakich okresach cena złota w PLN osiągała najwyższe
   i najniższe wartości oraz jak obecna cena wypada na ich tle?

3. Czy po silnym wzroście lub spadku ceny występowała kontynuacja ruchu, czy jego odwrócenie?

4. Czy kursy walut i wybrane wskaźniki makroekonomiczne poprawiają prognozę względem modelu wykorzystującego wyłącznie historię złota?

5. Jak duży był historyczny błąd prognozy i czy model poprawnie
   przewidywał kierunek zmiany ceny?

## 2. Zmienne i źródła

### Zmienne

| Zmienna | Źródło / identyfikator |
| --- | --- |
| Historyczna cena złota w PLN/g | NBP, `cenyzlota` |
| Średni kurs dzienny USD/PLN | NBP, `USD` |
| Średni kurs dzienny EUR/PLN | NBP, `EUR` |
| Średni kurs dzienny CHF/PLN | NBP, `CHF` |
| Nominalna rentowność obligacji skarbowych USA, 10 lat | FRED, `DGS10` |
| Nominalna rentowność obligacji skarbowych USA, 2 lata | FRED, `DGS2` |
| Realna rentowność obligacji skarbowych USA indeksowanych inflacją, 10 lat | FRED, `DFII10` |
| Efektywna stopa funduszy federalnych | FRED, `DFF` |
| 10-letnia stopa breakeven, miara oczekiwań inflacyjnych | FRED, `T10YIE` |
| Indeks zmienności rynku akcji VIX | FRED, `VIXCLS` |
| Cena ropy naftowej WTI | FRED, `DCOILWTICO` |
| Indeks NASDAQ Composite | FRED, `NASDAQCOM` |
| Indeks cen konsumpcyjnych w USA | FRED, `CPIAUCSL` |
| Stopa bezrobocia w USA | FRED, `UNRATE` |

**Zmienna objaśniana:** cena złota NBP w PLN/g.

**Horyzont prognozy:** kolejny dzień publikacji notowania.

### Źródła

1. [NBP Web API — dokumentacja cen złota i kursów walut](https://api.nbp.pl/).
2. [FRED API — dokumentacja](https://fred.stlouisfed.org/docs/api/fred/).
3. [FRED — metadane szeregów czasowych](https://fred.stlouisfed.org/). Definicje każdej serii należy sprawdzić pod jej identyfikatorem.
4. [FRED — daty wersji szeregu](https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html).

## 3. Architektura i przepływ danych

### Warstwy przechowywania

- **Raw:** oryginalne odpowiedzi JSON oraz źródło, parametry zapytania i czas pobrania. Planowany zapis w `data/raw/`.
- **Clean:** rekordy po konwersji typów, ujednoliceniu jednostek i kontroli jakości. Planowane przechowywanie w tabelach bazy danych.
- **Serving:** osobno zapisane dane analityczne, statystyki i wyniki prognoz używane przez dashboard.

Nieudana aktualizacja danych nie powinna zastępować ostatnich poprawnych danych.

## 4. Transformacje i model analityczny

Transformacje zbioru danych obejmują:

1. Konwersję dat i wartości liczbowych oraz ujednolicenie nazw pól.
2. Sprawdzenie kompletności i unikalności rekordów.
3. Uporządkowanie szeregów według daty.
4. Połączenie danych z uwzględnieniem dat.
5. Wyznaczenie statystyk i cech do prognozowania.
6. Przygotowanie zestawu danych zasilającego aplikację.

Jedna obserwacja zbioru prognostycznego będzie odpowiadać jednemu dniowi publikacji ceny złota. Dla wskaźników publikowanych rzadziej uwzględnimy najnowszą informację faktycznie dostępną w chwili prognozy. Nie będziemy przypisywać późniejszych publikacji do wcześniejszych prognoz. Obsługa rewizji i danych historycznie dostępnych zostanie udokumentowana; FRED udostępnia mechanizmy dat wersji danych.

### Ocena prognoz modelu

Punktem odniesienia będzie prognoza równa ostatniej znanej cenie. Planowane miary to MAE i RMSE w PLN/g. Porównamy wariant wykorzystujący historię złota z wariantami zawierającymi dodatkowe zmienne. Konkretne algorytmy i wyniki zostaną opisane po przeprowadzeniu eksperymentów.

## 5. Kontrola jakości

### *soon*

## 6. Cztery perspektywy projektu

### Biznesowa

### Dziedzinowa

### Techniczna

### Prawna i etyczna

## 7. Struktura repozytorium

### *soon.*

## 8. Instalacja i uruchomienie

### *soon..*

## 9. Ograniczenia i rozwój

### *soon...*
