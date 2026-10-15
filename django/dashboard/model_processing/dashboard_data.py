import pickle

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .create_model import calculate_metrics


def simulate_investment(df):

    df = df.copy()

    # Faktyczna zmiana ceny pomiędzy t a t+1.
    daily_return = df["actual"] / df["previous"] - 1

    # Prognoza wzrostu -> złoto, pozostałe przypadki -> gotówka.
    position = (df["predicted"] > df["previous"]).astype(int)

    df["model_capital"] = (
        10_000 * (1 + position * daily_return).cumprod()
    )

    df["hold_capital"] = (
        10_000 * (1 + daily_return).cumprod()
    )

    return df


def make_chart(df, columns, y_title, include_js=False):

    fig = go.Figure()

    for column, label in columns.items():
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[column],
                name=label,
                mode="lines",
            )
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        yaxis_title=y_title,
        hovermode="x unified",
        height=400,
        margin=dict(l=55, r=20, t=40, b=40),
        legend=dict(orientation="h"),
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs=True if include_js else False,
        config={"responsive": True, "displaylogo": False},
    )


def prepare_dashboard(models_dir, period="1"):

    files = sorted(models_dir.glob("*/model.pkl"))

    if not files:
        raise ValueError("Najpierw wytrenuj i zapisz model.")

    model_path = files[-1]

    with model_path.open("rb") as file:
        saved = pickle.load(file)

    # Dane były skalowane przed zapisem — nie skalujemy ich ponownie.
    predictions = saved["model"].predict(saved["X_test"])

    df = pd.DataFrame({
        "date": pd.to_datetime(saved["dates_test"]),
        "actual": saved["y_test"],
        "predicted": predictions,
        "previous": saved["baseline_test"],
    }).sort_values("date").reset_index(drop=True)

    metrics = calculate_metrics(df["actual"], df["predicted"])

    baseline_metrics = calculate_metrics(
        df["actual"],
        df["previous"],
    )

    actual_direction = np.sign(df["actual"] - df["previous"])
    predicted_direction = np.sign(df["predicted"] - df["previous"])

    accuracy = (
        (actual_direction == predicted_direction).mean() * 100
    )

    # Okresy liczymy od końca testu, a nie od dzisiejszej daty.
    end_date = df["date"].max()

    returns = []

    for months in [6, 3, 2, 1]:

        start_date = end_date - pd.DateOffset(months=months)

        row = {
            "months": months,
            "available": df["date"].min() <= start_date,
        }

        if row["available"]:

            subset = df.loc[df["date"] > start_date]
            simulation = simulate_investment(subset)

            row["model_return"] = (
                simulation["model_capital"].iloc[-1] / 10_000 - 1
            ) * 100

            row["hold_return"] = (
                simulation["hold_capital"].iloc[-1] / 10_000 - 1
            ) * 100

        returns.append(row)

    # Filtr zmienia zakres obu wykresów.
    if period not in {"all", "6", "3", "2", "1"}:
        period = "1"

    chart_df = df.copy()

    if period != "all":

        start_date = end_date - pd.DateOffset(months=int(period))

        chart_df = chart_df.loc[
            chart_df["date"] > start_date
        ].copy()

    simulation = simulate_investment(chart_df)

    price_chart = make_chart(
        chart_df,
        {
            "actual": "Cena rzeczywista",
            "predicted": "Prognoza modelu",
        },
        "PLN / g",
        include_js=True,
    )

    capital_chart = make_chart(
        simulation,
        {
            "model_capital": "Strategia modelu",
            "hold_capital": "Kup i trzymaj",
        },
        "Wartość kapitału / PLN",
    )

    recent = df.tail(10).iloc[::-1].copy()

    recent["error"] = recent["predicted"] - recent["actual"]

    recent["direction_ok"] = (
        np.sign(recent["predicted"] - recent["previous"])
        == np.sign(recent["actual"] - recent["previous"])
    )

    return {
        "model_name": model_path.parent.name,
        "start_date": df["date"].min(),
        "end_date": end_date,
        "metrics": metrics,
        "baseline_metrics": baseline_metrics,
        "accuracy": accuracy,
        "price_chart": price_chart,
        "capital_chart": capital_chart,
        "recent": recent.to_dict("records"),
        "returns": returns,
        "period": period,
    }