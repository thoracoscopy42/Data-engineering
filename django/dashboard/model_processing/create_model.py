import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import ParameterGrid

def prepare_model_data(df):
    
    required = {"date", "gold"}

    if not required.issubset(df.columns):
        raise ValueError("Brakuje podstawowych kolumn.")

    df = df.sort_values("date").reset_index(drop=True).copy()

    if df["date"].isna().any():
        raise ValueError("Daty mają jakieś brakujące wiersze.")


    duplicates = df[df["date"].duplicated(keep=False)]

    if not duplicates.empty:
        print(
            duplicates.sort_values("date").to_string(index=False),
            flush=True,
        )


    features = df.drop(columns=["date"])

    if not all(pd.api.types.is_numeric_dtype(dtype)
               for dtype in features.dtypes):
        raise ValueError("Nie wszystkie dane są liczbowe.")

    if not np.isfinite(features.to_numpy(dtype=float)).all():
        raise ValueError("Dane zawierają NaN lub wartości nieskończone.")

    X = features.iloc[:-1].reset_index(drop=True)
    y = df["gold"].iloc[1:].reset_index(drop=True)

    target_dates = df["date"].iloc[1:].reset_index(drop=True)
    baseline = df["gold"].iloc[:-1].reset_index(drop=True)

    train_end = int(len(X) * 0.7)
    val_end   = int(len(X) * 0.9)

    ranges = {
        "train": slice(0, train_end),
        "val":   slice(train_end, val_end),
        "test":  slice(val_end, len(X)),
    }

    for rows in ranges.values():
        if len(X.iloc[rows]) < 2:
            raise ValueError("za mało danych.")

    scaler = StandardScaler()

    scaler.fit(X.iloc[ranges["train"]])

    model_data ={
        "scaler": scaler,
        "feature_names": X.columns.tolist(),
    }

    for name, rows in ranges.items():
        model_data[f"X_{name}"]         = scaler.transform(X.iloc[rows])
        model_data[f"y_{name}"]         = y.iloc[rows].to_numpy()
        model_data[f"dates_{name}"]     = target_dates.iloc[rows].to_numpy()
        model_data[f"baseline_{name}"]  = baseline.iloc[rows].to_numpy()


    return model_data

def train_model(model_data, scale_target=False):


    param_grid = {
        "hidden_layer_sizes": [(32, 16), (64, 32), (128, 64), (8, 4, 2)],
        "alpha": [0.001, 0.01],
        "learning_rate_init": [0.0005, 0.001],
        "batch_size": ['auto', 18, 32]
    }

    configurations = list(ParameterGrid(param_grid))

    best_model = None
    best_params = None
    best_mae = float("inf")

    results = []


    for number, params in enumerate(configurations, start=1):
        print(
            f"Konfiguracja {number}/{len(configurations)}: {params}",
            flush=True,
        )

        model = MLPRegressor(
            random_state=42,
            activation="relu",
            solver="adam",
            max_iter=5000,
            early_stopping=False,
            n_iter_no_change=25,
            tol=0.0001,
            **params,
        )

        if scale_target:
            model = TransformedTargetRegressor(
                regressor=model,
                transformer=StandardScaler(),
            )

        model.fit(
            model_data["X_train"],
            model_data["y_train"],
        )

        predictions = model.predict(model_data["X_val"])

        mae = mean_absolute_error(
            model_data["y_val"],
            predictions,
        )

        # Dostęp do wytrenowanego MLP również przy skalowaniu y.
        mlp = model.regressor_ if scale_target else model

        results.append({
            **params,
            "MAE_val": float(mae),
            "epochs": mlp.n_iter_,
        })

        print(
            f"MAE walidacji: {mae:.4f} PLN/g, "
            f"epoki: {mlp.n_iter_}",
            flush=True,
        )

        if mae < best_mae:
            best_mae = mae
            best_params = params.copy()
            best_model = model

    ranking = pd.DataFrame(results).sort_values("MAE_val")

    print("\nRanking konfiguracji:", flush=True)
    print(ranking.to_string(index=False), flush=True)

    print(f"\nNajlepsze parametry: {best_params}", flush=True)
    print(f"Najlepsze MAE walidacji: {best_mae:.4f}", flush=True)

    return best_model

def calculate_metrics(y_true, y_pred):

    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt((mean_squared_error(y_true, y_pred)))),
        "R2": float(r2_score(y_true, y_pred)),
    }

def evaluate_model(model, model_data, split="val"):

    if split not in {"train", "val", "test"}:
        raise ValueError("??? co to za zbiór danych")

    y_true = model_data[f"y_{split}"]
    y_pred = model.predict(model_data[f"X_{split}"])
    baseline = model_data[f"baseline_{split}"]

    predictions = pd.DataFrame({
        "date": model_data[f"dates_{split}"],
        "gold_actual": y_true,
        "gold_prediceted": y_pred,
        "gold_baseline": baseline,
    })
    
    return {
        "split": split,
        "model_metrics": calculate_metrics(y_true, y_pred),
        "baseline_metrics": calculate_metrics(y_true, baseline),
        "predictions": predictions,
    }

def create_model(df, scale_target=False):

    model_data = prepare_model_data(df)
    model = train_model(model_data, scale_target=scale_target)
    results = evaluate_model(model, model_data, split="val")

    return model, model_data, results