
import json
import requests

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .data_sources.nbp import fetch_gold, fetch_currency
from .data_sources.fred import fetch_series

@require_http_methods(["GET", "POST"])
def index(request):
    
    context = {}

    if request.method == "POST":
        if request.POST.get("action") == "fetch_all":

            try:
                data = fetch_all()

                counts = {
                    name: len(records)
                    for name, records in data.items()
                }

                print("Liczba pobranych rekordów:", counts, flush=True)

                context["message"] = (
                    f"Pobrano: "
                    f"złoto - {counts['gold']}, "
                    f"USD   - {counts['usd']}, "
                    f"EUR   - {counts['eur']}, "
                    f"CHF   - {counts['chf']}, "
                    f"DFII10 - {counts['DFII10']}, "
                    f"DGS10 - {counts['DGS10']}, "
                    f"DGS2 - {counts['DGS2']}, "
                    f"DFF - {counts['DFF']}, "
                    f"T10YIE - {counts['T10YIE']}, "
                    f"VIXCLS - {counts['VIXCLS']}, "
                    f"DCOILWTICO - {counts['DCOILWTICO']}, "
                    f"NASDAQCOM - {counts['NASDAQCOM']}, "
                    f"CPIAUCSL - {counts['CPIAUCSL']}, "
                    f"UNRATE - {counts['UNRATE']}."
                )

            except (requests.exceptions.RequestException, ValueError) as exc:
                print(f"Błąd pobierania: {exc}", flush=True)

                context["error"] = (
                    "Nie udało się pobrać wszystkich danych. "
                    "Sprawdź szczegóły w terminalu."
                )
        else:
            context["error"] = "Nieznana akcja."

    return render(request, "index.html", context)

def fetch_all():
    return {
        "gold": fetch_gold(),
        "usd":  fetch_currency("usd"),
        "eur":  fetch_currency("eur"),
        "chf":  fetch_currency("chf"),
        "DFII10": fetch_series("DFII10"),
        "DGS10": fetch_series("DGS10"),
        "DGS2": fetch_series("DGS2"),
        "DFF": fetch_series("DFF"),
        "T10YIE": fetch_series("T10YIE"),
        "VIXCLS": fetch_series("VIXCLS"),
        "DCOILWTICO": fetch_series("DCOILWTICO"),
        "NASDAQCOM": fetch_series("NASDAQCOM"),
        "CPIAUCSL": fetch_series("CPIAUCSL"),
        "UNRATE": fetch_series("UNRATE"),
    }