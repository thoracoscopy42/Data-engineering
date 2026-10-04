
import json
import requests

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .data_sources.nbp import fetch_gold, fetch_currency

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
                    f"złoto - {counts['gold']},"
                    f"USD   - {counts['usd']}, "
                    f"EUR   - {counts['eur']}, "
                    f"CHF   - {counts['chf']}."
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
    }