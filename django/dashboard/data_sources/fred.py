from datetime import date

import requests
from django.conf import settings


def fetch_series(series_id):
    api_key = settings.FRED_API_KEY

    if not api_key:
        raise ValueError("Uzupełnij FRED_KEY w pliku .env.")

    end = date.today()

    try:
        start = end.replace(year=end.year - 13)
    except ValueError:
        start = end.replace(year=end.year - 13, day=28)

    response = requests.get(
        "https://api.stlouisfed.org/fred/series/observations",
        params={
            "api_key": api_key,
            "series_id": series_id,
            "file_type": "json",
            "observation_start": start.isoformat(),
            "observation_end": end.isoformat(),
            "sort_order": "asc",
            "limit": 100000,
        },
        timeout=30,
    )

    if not response.ok:
        raise requests.exceptions.RequestException(
            f"FRED: błąd HTTP {response.status_code} "
            f"dla serii {series_id}."
        )

    data = response.json()
    records = data["observations"]

    print(
        f"FRED {series_id}: pobrano {len(records)} obserwacji.",
        flush=True,
    )

    return records