from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "housing.csv"
MODEL_FILE = BASE_DIR / "model.pkl"
PIPELINE_FILE = BASE_DIR / "pipeline.pkl"

NUMERIC_FIELDS = [
    {
        "name": "longitude",
        "label": "Longitude",
        "step": "0.01",
        "required": True,
        "example": "-118.39",
    },
    {
        "name": "latitude",
        "label": "Latitude",
        "step": "0.01",
        "required": True,
        "example": "34.12",
    },
    {
        "name": "housing_median_age",
        "label": "Housing Median Age",
        "step": "1",
        "required": True,
        "example": "29",
    },
    {
        "name": "total_rooms",
        "label": "Total Rooms",
        "step": "1",
        "required": True,
        "example": "3200",
    },
    {
        "name": "total_bedrooms",
        "label": "Total Bedrooms",
        "step": "1",
        "required": False,
        "help": "Optional — leave blank if unknown.",
        "example": "650",
    },
    {
        "name": "population",
        "label": "Population",
        "step": "1",
        "required": True,
        "example": "1500",
    },
    {
        "name": "households",
        "label": "Households",
        "step": "1",
        "required": True,
        "example": "540",
    },
    {
        "name": "median_income",
        "label": "Median Income",
        "step": "0.0001",
        "required": True,
        "example": "5.2800",
    },
]

FEATURE_ORDER = [field["name"] for field in NUMERIC_FIELDS] + ["ocean_proximity"]


def build_pipeline(num_attributes, cat_attributes):
    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_pipeline = Pipeline(
        [
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        [
            ("num", num_pipeline, num_attributes),
            ("cat", cat_pipeline, cat_attributes),
        ]
    )


def train_model():
    housing = pd.read_csv(DATA_FILE)
    housing.columns = housing.columns.str.strip()

    housing["income_cat"] = pd.cut(
        housing["median_income"],
        bins=[0.0, 1.5, 3.0, 4.5, 6.0, np.inf],
        labels=[1, 2, 3, 4, 5],
    )

    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, _ in split.split(housing, housing["income_cat"]):
        strat_train_set = housing.iloc[train_index].drop("income_cat", axis=1)

    housing_train = strat_train_set.copy()
    housing_features = housing_train.drop("median_house_value", axis=1)
    housing_labels = housing_train["median_house_value"].copy()

    num_attributes = housing_features.drop("ocean_proximity", axis=1).columns.tolist()
    cat_attributes = ["ocean_proximity"]

    preprocessor = build_pipeline(num_attributes, cat_attributes)
    housing_prepared = preprocessor.fit_transform(housing_features)

    model = RandomForestRegressor(random_state=42)
    model.fit(housing_prepared, housing_labels)

    joblib.dump(model, MODEL_FILE)
    joblib.dump(preprocessor, PIPELINE_FILE)

    return model, preprocessor


def ensure_model():
    if MODEL_FILE.exists() and PIPELINE_FILE.exists():
        try:
            return joblib.load(MODEL_FILE), joblib.load(PIPELINE_FILE)
        except Exception:
            pass

    return train_model()


def get_ocean_options():
    ocean_data = pd.read_csv(DATA_FILE, usecols=["ocean_proximity"])
    options = (
        ocean_data["ocean_proximity"]
        .astype(str)
        .str.strip()
        .replace("nan", np.nan)
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(options)


def parse_float(raw_value, label, required=True):
    if raw_value == "":
        if required:
            raise ValueError(f"{label} is required.")
        return np.nan

    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid number.") from exc


MODEL, PREPROCESSOR = ensure_model()
OCEAN_OPTIONS = get_ocean_options()


@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    error = None

    form_values = {field["name"]: "" for field in NUMERIC_FIELDS}
    selected_ocean = OCEAN_OPTIONS[0] if OCEAN_OPTIONS else ""

    if request.method == "POST":
        try:
            input_row = {}

            for field in NUMERIC_FIELDS:
                raw_value = request.form.get(field["name"], "").strip()
                form_values[field["name"]] = raw_value
                input_row[field["name"]] = parse_float(
                    raw_value,
                    field["label"],
                    required=field.get("required", True),
                )

            selected_ocean = request.form.get("ocean_proximity", "").strip()
            if selected_ocean not in OCEAN_OPTIONS:
                raise ValueError("Please select a valid ocean proximity value.")

            input_row["ocean_proximity"] = selected_ocean
            input_df = pd.DataFrame([input_row], columns=FEATURE_ORDER)

            transformed_input = PREPROCESSOR.transform(input_df)
            predicted_price = float(MODEL.predict(transformed_input)[0])
            prediction = f"${predicted_price:,.2f}"

        except ValueError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        numeric_fields=NUMERIC_FIELDS,
        ocean_options=OCEAN_OPTIONS,
        selected_ocean=selected_ocean,
        form_values=form_values,
        prediction=prediction,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)