import json

from datetime import datetime, timezone

from django.conf import settings

import numpy 
import pandas

DATA_DIR = settings.BASE_DIR / "data"

def save_raw(data):

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%d_%H%M%S_%f")

    folder = DATA_DIR / "raw"
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{run_id}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "downloaded_at": now.isoformat(),
                "data": data,
            },
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print(f"Zapisano raw: {path}", flush=True)

    return run_id

def save_clean(tables, run_id):
    
    folder = DATA_DIR / "clean" / run_id
    folder.mkdir(parents=True, exist_ok=True)

    for name, df in tables.items():
        path = folder /f"{name}.csv"

        df.to_csv(
            path,
            index=False,
            encoding = "utf-8",
            date_format="%Y-%m-%d",
            na_rep="",
        )

    print(f"Zapisano: {path}", flush=True)


    return {}

def save_serving(df, run_id):
    
    folder = DATA_DIR / "serving"
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{run_id}_merged.csv"


    df.to_csv(
        path,
        index=False,
        encoding = "utf-8",
        date_format="%Y-%m-%d",
        na_rep="",
    )

    print(
        f"Zapisano serving: {path}"
        f"Wiersze: {len(df)}, kolumny: {len(df.columns)}.",
        flush=True,
    )
    
    return path