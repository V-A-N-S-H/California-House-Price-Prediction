import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Load model, pipeline, and dataset
MODEL_FILE = "model.pkl"
PIPELINE_FILE = "pipeline.pkl"
DATA_FILE = "housing.csv"

# Load ML assets
if os.path.exists(MODEL_FILE) and os.path.exists(PIPELINE_FILE):
    model = joblib.load(MODEL_FILE)
    pipeline = joblib.load(PIPELINE_FILE)
    model_loaded = True
else:
    model_loaded = False
    print("WARNING: Model and pipeline files not found! Prediction API will be unavailable.")

# Load housing dataset
if os.path.exists(DATA_FILE):
    df_raw = pd.read_csv(DATA_FILE)
    # Strip column names just in case
    df_raw.columns = df_raw.columns.str.strip()
    data_loaded = True
else:
    df_raw = pd.DataFrame()
    data_loaded = False
    print("WARNING: housing.csv dataset not found!")

# Cache processed statistics for the dashboard
cached_stats = {}
map_sample_data = []

def precompute_statistics():
    global cached_stats, map_sample_data
    if not data_loaded:
        return
    
    # 1. Basic KPI metrics
    cached_stats["kpis"] = {
        "total_records": int(len(df_raw)),
        "avg_house_value": float(df_raw["median_house_value"].mean()),
        "median_house_value": float(df_raw["median_house_value"].median()),
        "avg_income": float(df_raw["median_income"].mean() * 10000),  # Convert to actual dollars
        "avg_age": float(df_raw["housing_median_age"].mean()),
        "total_population": int(df_raw["population"].sum())
    }

    # 2. Correlation Matrix (Numerical variables only)
    num_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
    corr_matrix = df_raw[num_cols].corr().round(2)
    # Convert correlation matrix to ECharts suitable format
    cached_stats["correlation"] = {
        "columns": num_cols,
        "values": corr_matrix.values.tolist()
    }

    # 3. Ocean Proximity Stats (Bar Chart data)
    ocean_group = df_raw.groupby("ocean_proximity").agg(
        avg_price=("median_house_value", "mean"),
        avg_income=("median_income", "mean"),
        count=("median_house_value", "count")
    ).round(2).reset_index()
    
    cached_stats["ocean_proximity_stats"] = {
        "categories": ocean_group["ocean_proximity"].tolist(),
        "avg_prices": ocean_group["avg_price"].tolist(),
        "avg_incomes": (ocean_group["avg_income"] * 10000).tolist(),
        "counts": ocean_group["count"].tolist()
    }

    # 4. Income vs House Value distribution for Scatter plot
    # To prevent browser lockup, we sample 1000 points specifically for scatter analytics
    scatter_df = df_raw.sample(n=min(1000, len(df_raw)), random_state=42)
    cached_stats["scatter_data"] = scatter_df[["median_income", "median_house_value", "housing_median_age"]].values.tolist()

    # 5. Price range distribution (Histogram data)
    prices = df_raw["median_house_value"].dropna()
    counts, bins = np.histogram(prices, bins=15)
    cached_stats["price_distribution"] = {
        "counts": counts.tolist(),
        "bins": [float(b) for b in bins]
    }

    # 6. Map Sample Points (Downsampled coordinates for Leaflet map to prevent lag)
    # Stratified-like representation: Sample ~1,500 points uniformly across the dataset
    map_df = df_raw.sample(n=min(1500, len(df_raw)), random_state=42)
    map_sample_data = map_df[[
        "longitude", "latitude", "median_house_value", 
        "median_income", "housing_median_age", "ocean_proximity"
    ]].to_dict(orient="records")

# Run precomputation at startup
if data_loaded:
    precompute_statistics()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/statistics")
def get_statistics():
    if not data_loaded:
        return jsonify({"error": "Dataset not available"}), 500
    return jsonify(cached_stats)

@app.route("/api/map-data")
def get_map_data():
    if not data_loaded:
        return jsonify({"error": "Dataset not available"}), 500
    return jsonify(map_sample_data)

@app.route("/api/predict", methods=["POST"])
def predict():
    if not model_loaded:
        return jsonify({"error": "Model or preprocessing pipeline not loaded"}), 500
    
    try:
        req_data = request.get_json()
        
        # Verify required keys are present
        required_features = [
            "longitude", "latitude", "housing_median_age", 
            "total_rooms", "total_bedrooms", "population", 
            "households", "median_income", "ocean_proximity"
        ]
        
        missing = [f for f in required_features if f not in req_data]
        if missing:
            return jsonify({"error": f"Missing required parameters: {', '.join(missing)}"}), 400
        
        # Parse inputs into structured DataFrame for sklearn pipeline
        input_dict = {
            "longitude": [float(req_data["longitude"])],
            "latitude": [float(req_data["latitude"])],
            "housing_median_age": [float(req_data["housing_median_age"])],
            "total_rooms": [float(req_data["total_rooms"])],
            "total_bedrooms": [float(req_data["total_bedrooms"])],
            "population": [float(req_data["population"])],
            "households": [float(req_data["households"])],
            "median_income": [float(req_data["median_income"])],
            "ocean_proximity": [str(req_data["ocean_proximity"]).strip()]
        }
        
        df_input = pd.DataFrame(input_dict)
        
        # Pass DataFrame through the transformer pipeline
        transformed = pipeline.transform(df_input)
        
        # Make prediction
        prediction = model.predict(transformed)[0]
        
        # Format the output price cleanly
        predicted_value = float(np.round(prediction, 2))
        
        return jsonify({
            "success": True,
            "predicted_price": predicted_value,
            "formatted_price": f"${predicted_value:,.2f}"
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
