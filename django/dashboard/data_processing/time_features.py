def add_time_features(df):

    df = df.sort_values("date").reset_index(drop=True).copy()

    for lag in [1, 7, 14]:
        df[f"gold_lag_{lag}"] = df["gold"].shift(lag)

    df["gold_change_pct"] = (
        df["gold"].pct_change(fill_method=None)*100
    )

    return df
