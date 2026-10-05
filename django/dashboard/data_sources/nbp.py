
from datetime import date, timedelta
import requests


def fetch_gold():
    end = date.today()

    # Ta sama data 10 lat wcześniej.
    # Dla 29 lutego przyjmujemy 28 lutego.
    try:
        start = end.replace(year=end.year - 13)
    except ValueError:
        start = end.replace(year=end.year - 13, day=28)

    records = []

    with requests.Session() as session:
        while start <= end:
            chunk_end = min(start + timedelta(days=92), end)

            url = (
                "https://api.nbp.pl/api/cenyzlota/"
                f"{start.isoformat()}/{chunk_end.isoformat()}/"
            )

            response = session.get(
                url,
                params={"format": "json"},
                timeout=15,
            )

            if response.status_code != 404:
                response.raise_for_status()
                records.extend(response.json())

            print(
                f"Zakres: {start} – {chunk_end}. "
                f"Łącznie: {len(records)} notowań.",
                flush=True,
            )

            start = chunk_end + timedelta(days=1)

    return sorted(records, key=lambda row: row["data"])



def fetch_currency(code):
    code = code.lower()

    end = date.today()

    try:
        start = end.replace(year=end.year - 13)
    except ValueError:
        start = end.replace(year=end.year - 13, day=28)

    records = []

    with requests.Session() as session:
        while start <= end:
            chunk_end = min(start + timedelta(days=92), end)

            url = (
                "https://api.nbp.pl/api/exchangerates/rates/"
                f"a/{code}/{start.isoformat()}/{chunk_end.isoformat()}/"
            )

            response = session.get(
                url,
                params={"format": "json"},
                timeout=15,
            )

            if response.status_code != 404:
                response.raise_for_status()

                
                records.extend(response.json()["rates"])

            print(
                f"{code.upper()}: {start} - {chunk_end}. "
                f"Łącznie: {len(records)} notowań.",
                flush=True,
            )

            start = chunk_end + timedelta(days=1)

    return sorted(records, key=lambda row: row["effectiveDate"])
