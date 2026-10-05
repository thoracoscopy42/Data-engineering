import numpy as np
import pandas as pd


def clean_series(records, date_field, value_field, name):

    if not records:
        raise ValueError(f"{name}: nie ma rekordów.")

    df = pd.DataFrame(records)

    required = {date_field, value_field}

    if not required.issubset(df.columns):
        raise ValueError(f"{name}: Nie ma wymaganych kolumn - date i value")

    df = df[[date_field, value_field]].copy()
    df.columns = ["date", name]

    # unifikacja dat

    df["date"] = pd.to_datetime(
        df["date"],
        format="%Y-%m-%d",
        errors="raise",
    )

    # zmiana "." z FRED na brak wartości

    values = df[name].replace(".", np.nan)

    df[name] = pd.to_numeric(
        values,
        errors="raise",
    ).astype(float)

    # powtarzające się i brakujące daty 

    if df["date"].isna().any():
        raise ValueError(f"{name}: brakujące daty.")

    if df["date"].duplicated().any():
        raise ValueError(f"{name}: powtarzające się daty.")

    available_values = df[name].dropna()

    if available_values.empty:
        raise ValueError(f"{name}: jakimś cudem wszystkie wartości były brakujące")

    if not np.isfinite(available_values).all():
        raise ValueError("{name}: w zbiorze istnieją jakieś infinite value?????!?!?!?")

    # dodatnie wartości dla złota i kursów

    if name in {"gold", "eur", "chf", "usd"}:
        
        if df[name].isna().any():
            raise ValueError(f"{name}: jakimś cudem są tu brakujące wartości w walutach/złocie")

        if (df[name] <= 0).any():
            raise ValueError(f"{name}: how did we get here?")
        

    df = df.sort_values("date").reset_index(drop=True)

    print(
        f"{name}: {len(df)} rekordów, "
        f"braki: {df[name].isna().sum()}",
        flush=True
    )
    
    
    return df

def clean_all(data):

    tables = {}

    for name, records in data.items():
        if name =="gold":
            date_field = "data"
            value_field = "cena"

        elif name in {"eur", "usd", "chf"}:
            date_field = "effectiveDate"
            value_field = "mid"

        else:
            date_field = "date"
            value_field = "value"

        tables[name] = clean_series(
            records=records,
            date_field=date_field,
            value_field=value_field,
            name=name,
        )

    return tables

def merge_series(tables):

    merged = tables["gold"].copy()

    for name, df in tables.items():
        if name =="gold":
            continue

        merged = merged.merge(
            df,
            on="date",
            how="left",
            validate="one_to_one",
        )

    merged = merged.sort_values("date").reset_index(drop=True)

    if len(merged) != len(tables["gold"]):
        raise ValueError("zmieniła się liczba rekordów złota")

    print("rozmiar:", merged.shape, flush=True)
    print("braki po połączeniu:", flush=True)
    print(merged.isna().sum(), flush=True)

    return merged

def prepare_data():
    
    return {}