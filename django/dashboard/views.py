
import json
import requests
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# sources
from .data_sources.nbp import fetch_gold, fetch_currency
from .data_sources.fred import fetch_series

# data processing
from .data_processing.data_storage import DATA_DIR, save_raw, save_clean, save_serving

from .data_processing.data_cleaning import clean_series, clean_all, merge_series, prepare_serving_data





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
        # "CPIAUCSL": fetch_series("CPIAUCSL"),
        # "UNRATE": fetch_series("UNRATE"),
    }


@require_http_methods(["GET", "POST"])
def index(request):
    
    context = {}

    if request.method == "POST":
        if request.POST.get("action") == "fetch_all":

            try:
                data = fetch_all()

                run_id = save_raw(data)

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
                    # f"CPIAUCSL - {counts['CPIAUCSL']}, "
                    # f"UNRATE - {counts['UNRATE']}."
                )

            except (requests.exceptions.RequestException, ValueError) as exc:
                print(f"Błąd pobierania: {exc}", flush=True)

                context["error"] = (
                    "Nie udało się pobrać wszystkich danych. "
                    "Sprawdź szczegóły w terminalu."
                )

        elif request.POST.get("action") == "clean_all":
            try:

                files = sorted((DATA_DIR / "raw").glob("*.json"))

                if not files:
                    raise ValueError("Brak danych w raw.")

                raw_path = files[-1]

                with raw_path.open("r", encoding="utf-8") as file:
                    snapshot = json.load(file)

                tables = clean_all(snapshot["data"])

                save_clean(tables, raw_path.stem)

                context["message"] = (
                    f"Oczyszczono {len(tables)} serii. "
                    f"Źródło: {raw_path.name}. "
                    f"Zapisano CSV w data/clean/{raw_path.stem}/."
                )

            except (ValueError, KeyError, TypeError, OSError) as exc:
                print(f"Błąd czyszczenia: {exc}", flush=True)

                context["error"] = f"Nie udało się oczyścić danych: {exc}"

        elif request.POST.get("action") == "prepare_serving":
            try: 
                clean_root = DATA_DIR / "clean"

                if not clean_root.exists():
                    raise ValueError(f"nie ma oczyszczonych danych.")

                folders = []

                for folder in clean_root.iterdir():
                    if folder.is_dir():
                        folders.append(folder)

                folders = sorted(folders)

                if not folders:
                    raise ValueError("Nie ma żadnych folderów w clean.")

                clean_dir = folders[-1]
                csv_files = sorted(clean_dir.glob("*.csv"))

                expected ={
                    "gold", "usd", "eur", "chf",
                    "DFII10", "DGS10", "DGS2", "DFF", "T10YIE",
                    "VIXCLS", "DCOILWTICO", "NASDAQCOM",
                    # "CPIAUCSL", "UNRATE",
                    }

                available = {path.stem for path in csv_files}
                missing = expected - available

                if missing:
                    raise ValueError(
                        f"Niekompletny zakres danych."
                        f"{', '.join(sorted(missing))}."
                    )
                tables = {}

                for path in csv_files:
                    if path.stem in expected:
                        tables[path.stem] = pd.read_csv(
                            path,
                            parse_dates=["date"],
                        )

                merged = merge_series(tables)
                prepared = prepare_serving_data(merged, tables)
                path = save_serving(prepared, clean_dir.name)


            except (ValueError, KeyError, OSError) as exc:
                print(f"Błąd przygotowania serving: {exc}", flush=True)
                context["error"] = (
                    f"Nie udało się przygotować danych analitycznych: {exc}"
                )

        else:
            context["error"] = "Nieznana akcja."

    return render(request, "index.html", context)

