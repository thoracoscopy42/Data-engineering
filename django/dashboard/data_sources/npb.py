import requests

def fetch_gold():
    url = (
        "https://api.nbp.pl/api/cenyzlota/"
        "2025-01-01/2025-01-31/"
    )

    response = requests.get(
        url,
        params={"format": "json"},
        timeout=15,
    )
    response.raise_for_status()

    return response.json()