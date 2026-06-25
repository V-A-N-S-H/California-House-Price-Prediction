import streamlit as st
import pandas as pd
import numpy as np
import joblib
from streamlit_echarts import st_echarts
import textwrap

# ----------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# ----------------------------------------------------------------
st.set_page_config(
    page_title="California Housing Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    """Injects our custom CSS to override Streamlit's default styling to match our glassmorphic premium UI."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global Streamlit Overrides */
    .stApp {
        background-color: #090d16;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling Override */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 15, 30, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }
    
    /* Hide Streamlit Top Bar & Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Custom Glassmorphic Metric Cards */
    .kpi-card {
        background: rgba(17, 25, 40, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        opacity: 0;
        transition: all 0.3s ease;
    }
    .kpi-card:hover::before { opacity: 1; }
    
    .kpi-header {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #f3f4f6;
    }

    /* Result Glowing Box */
    .result-glowing-box {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.01);
        margin-top: 1rem;
    }
    .result-price {
        font-family: 'Outfit', sans-serif;
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Streamlit Button Override */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        padding: 0.5rem 2rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.25);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.4);
        color: white;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

inject_custom_css()

# ----------------------------------------------------------------
# 2. Global Data & ML Asset Loading
# ----------------------------------------------------------------
@st.cache_resource
def load_ml_assets():
    try:
        model = joblib.load("model.pkl")
        pipeline = joblib.load("pipeline.pkl")
        return model, pipeline
    except Exception as e:
        st.error(f"Could not load Machine Learning models: {e}")
        return None, None

@st.cache_data
def load_housing_data():
    try:
        df = pd.read_csv("housing.csv")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Failed to load housing dataset: {e}")
        return pd.DataFrame()

model, pipeline = load_ml_assets()
df_raw = load_housing_data()

# Precompute data slices for UI speed
if not df_raw.empty:
    df_scatter = df_raw.sample(n=min(1000, len(df_raw)), random_state=42)
    df_map = df_raw.sample(n=min(1500, len(df_raw)), random_state=42)
    ocean_group = df_raw.groupby("ocean_proximity").agg(
        avg_price=("median_house_value", "mean"),
        avg_income=("median_income", "mean")
    ).round(2).reset_index()


# ----------------------------------------------------------------
# 3. Sidebar UI
# ----------------------------------------------------------------
with st.sidebar:
    st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem;">
<div style="width: 36px; height: 36px; background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-family: 'Outfit'; color: white; box-shadow: 0 0 20px rgba(99,102,241,0.25);">CA</div>
<h1 style="font-family: 'Outfit'; font-size: 1.2rem; font-weight: 700; background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">Housing Analytics</h1>
</div>
""", unsafe_allow_html=True)
    
    view_selection = st.radio(
        "Navigation",
        options=["Overview Dashboard", "Interactive Map", "Price Predictor"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top: auto; padding-top: 2rem; color: #6b7280; font-size: 0.8rem; text-align: center; border-top: 1px solid rgba(255,255,255,0.07);'>California Housing Project<br>v2.0.0 • Streamlit Migration</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------
# 4. View: Overview Dashboard
# ----------------------------------------------------------------
if view_selection == "Overview Dashboard":
    st.markdown("<h2 style='font-family: Outfit; font-weight: 800;'>Overview Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Exploratory Data Analysis and key performance metrics for California housing records.</p>", unsafe_allow_html=True)
    
    # 4.1 KPIs
    if not df_raw.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
<div class="kpi-card">
<div class="kpi-header">Total Census Records</div>
<div class="kpi-value">{len(df_raw):,}</div>
</div>
""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
<div class="kpi-card">
<div class="kpi-header">Avg House Value</div>
<div class="kpi-value">${int(df_raw["median_house_value"].mean()):,}</div>
</div>
""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
<div class="kpi-card">
<div class="kpi-header">Avg Annual Income</div>
<div class="kpi-value">${int(df_raw["median_income"].mean() * 10000):,}</div>
</div>
""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
<div class="kpi-card">
<div class="kpi-header">Median Housing Age</div>
<div class="kpi-value">{int(df_raw["housing_median_age"].mean())} Yrs</div>
</div>
""", unsafe_allow_html=True)

        st.write("---")

        # 4.2 ECharts Graphs Row 1
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("<h4 style='font-family: Outfit; font-weight: 600;'>House Price Distribution</h4>", unsafe_allow_html=True)
            prices = df_raw["median_house_value"].dropna()
            counts, bins = np.histogram(prices, bins=15)
            xData = [f"${int(b/1000)}k" for b in bins[:-1]]
            
            option_dist = {
                "tooltip": { "trigger": "axis" },
                "xAxis": { "type": "category", "data": xData, "axisLabel": { "color": "#9ca3af" } },
                "yAxis": { "type": "value", "splitLine": { "lineStyle": { "color": "rgba(255,255,255,0.05)" } }, "axisLabel": { "color": "#9ca3af" } },
                "series": [{
                    "data": counts.tolist(),
                    "type": "bar",
                    "itemStyle": { "color": "#818cf8", "borderRadius": [4,4,0,0] }
                }]
            }
            st_echarts(options=option_dist, height="350px")

        with c2:
            st.markdown("<h4 style='font-family: Outfit; font-weight: 600;'>Average Price by Ocean Proximity</h4>", unsafe_allow_html=True)
            option_ocean = {
                "tooltip": { "trigger": "axis" },
                "legend": { "data": ["Avg House Value", "Avg Income"], "textStyle": {"color": "#9ca3af"} },
                "xAxis": { "type": "category", "data": ocean_group["ocean_proximity"].tolist(), "axisLabel": { "color": "#9ca3af" } },
                "yAxis": [
                    { "type": "value", "axisLabel": { "color": "#9ca3af" }, "splitLine": { "lineStyle": { "color": "rgba(255,255,255,0.05)" } } },
                    { "type": "value", "axisLabel": { "color": "#9ca3af" }, "splitLine": { "show": False } }
                ],
                "series": [
                    { "name": "Avg House Value", "type": "bar", "data": ocean_group["avg_price"].tolist(), "itemStyle": {"color": "#c084fc"} },
                    { "name": "Avg Income", "type": "line", "yAxisIndex": 1, "data": (ocean_group["avg_income"]*10000).tolist(), "itemStyle": {"color": "#10b981"}, "lineStyle": {"width": 3} }
                ]
            }
            st_echarts(options=option_ocean, height="350px")

        st.write("---")

        # 4.3 ECharts Graphs Row 2
        st.markdown("<h4 style='font-family: Outfit; font-weight: 600;'>Income vs. Median House Value Scatter Analysis</h4>", unsafe_allow_html=True)
        
        scatter_data = df_scatter[["median_income", "median_house_value", "housing_median_age"]].values.tolist()
        option_scatter = {
            "tooltip": { "trigger": "item" },
            "xAxis": { "type": "value", "name": "Median Income", "axisLabel": { "color": "#9ca3af" }, "splitLine": { "lineStyle": { "color": "rgba(255,255,255,0.05)" } } },
            "yAxis": { "type": "value", "name": "House Value", "axisLabel": { "color": "#9ca3af" }, "splitLine": { "lineStyle": { "color": "rgba(255,255,255,0.05)" } } },
            "visualMap": {
                "min": 1, "max": 52, "dimension": 2, "orient": "horizontal", "right": 10, "top": 10,
                "calculable": True, "text": ["52 Yrs", "1 Yr"],
                "inRange": { "color": ["#10b981", "#eab308", "#f97316", "#ef4444"] }, "textStyle": {"color": "#9ca3af"}
            },
            "series": [{
                "type": "scatter",
                "data": scatter_data,
                "symbolSize": 6,
                "itemStyle": { "opacity": 0.8 }
            }]
        }
        st_echarts(options=option_scatter, height="400px")

# ----------------------------------------------------------------
# 5. View: Interactive Map (Coordinate Scatter)
# ----------------------------------------------------------------
elif view_selection == "Interactive Map":
    st.markdown("<h2 style='font-family: Outfit; font-weight: 800;'>Geographic Coordinate Scatter Plot</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Explore spatial home valuations color-coded by median price mapped directly across Latitude and Longitude.</p>", unsafe_allow_html=True)
    
    if not df_raw.empty:
        formatted_data = df_map[[
            "longitude", "latitude", "median_house_value", 
            "median_income", "housing_median_age", "ocean_proximity"
        ]].values.tolist()

        option_geo = {
            "tooltip": { "trigger": "item" },
            "grid": { "top": "5%", "left": "5%", "right": "18%", "bottom": "8%", "containLabel": True },
            "xAxis": { 
                "type": "value", "name": "Longitude (Degrees West)", "nameLocation": "middle", "nameGap": 30,
                "nameTextStyle": { "color": "#9ca3af", "fontWeight": 600, "fontSize": 12 },
                "scale": True, "splitLine": { "lineStyle": { "color": "rgba(255,255,255,0.05)" } }, "axisLabel": { "color": "#9ca3af" }
            },
            "yAxis": { 
                "type": "value", "name": "Latitude (Degrees North)", "nameLocation": "middle", "nameGap": 40,
                "nameTextStyle": { "color": "#9ca3af", "fontWeight": 600, "fontSize": 12 },
                "scale": True, "splitLine": { "lineStyle": { "color": "rgba(255,255,255,0.05)" } }, "axisLabel": { "color": "#9ca3af" }
            },
            "visualMap": {
                "min": 15000, "max": 500001, "dimension": 2, "orient": "vertical", "right": 15, "top": "center",
                "text": ["$500k+", "$15k"], "calculable": True,
                "inRange": { "color": ["#6366f1", "#10b981", "#eab308", "#f97316", "#ef4444"] },
                "textStyle": { "color": "#9ca3af" }
            },
            "series": [{
                "name": "Census Tracts",
                "type": "scatter",
                "data": formatted_data,
                "symbolSize": 6,
                "itemStyle": { "opacity": 0.85, "shadowBlur": 2, "shadowColor": "rgba(0,0,0,0.5)" }
            }],
            "dataZoom": [{ "type": "inside", "disabled": False }]
        }
        st_echarts(options=option_geo, height="600px")

# ----------------------------------------------------------------
# 6. View: Price Predictor
# ----------------------------------------------------------------
elif view_selection == "Price Predictor":
    st.markdown("<h2 style='font-family: Outfit; font-weight: 800;'>Predictive Intelligence Model</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9ca3af;'>Configure micro-neighborhood housing attributes and compute home value predictions using Random Forest Regression.</p>", unsafe_allow_html=True)
    
    col_form, col_res = st.columns([1.2, 0.8], gap="large")
    
    with col_form:
        c1, c2 = st.columns(2)
        longitude = c1.number_input("Longitude", value=-122.23, step=0.01)
        latitude = c2.number_input("Latitude", value=37.88, step=0.01)
        
        housing_median_age = c1.slider("Median House Age (Years)", 1, 52, 28)
        median_income = c2.slider("Median Income (Scaled)", 0.5, 15.0, 3.8, 0.1)
        
        total_rooms = c1.slider("Total Rooms", 2, 10000, 2600, 10)
        total_bedrooms = c2.slider("Total Bedrooms", 1, 3000, 500, 5)
        
        population = c1.slider("Local Population", 3, 8000, 1400, 10)
        households = c2.slider("Households", 1, 3000, 500, 5)
        
        ocean_proximity = st.selectbox(
            "Ocean Proximity", 
            ["<1H OCEAN", "INLAND", "NEAR OCEAN", "NEAR BAY", "ISLAND"],
            index=2
        )
        
        predict_clicked = st.button("Execute Prediction Pipeline")
        
    with col_res:
        if predict_clicked:
            if model and pipeline:
                input_df = pd.DataFrame({
                    "longitude": [longitude],
                    "latitude": [latitude],
                    "housing_median_age": [housing_median_age],
                    "total_rooms": [total_rooms],
                    "total_bedrooms": [total_bedrooms],
                    "population": [population],
                    "households": [households],
                    "median_income": [median_income],
                    "ocean_proximity": [ocean_proximity]
                })
                
                transformed = pipeline.transform(input_df)
                prediction = model.predict(transformed)[0]
                
                st.markdown(f"""
<div style='background: rgba(17, 25, 40, 0.65); padding: 2rem; border-radius: 20px; border: 1px solid rgba(255,255,255,0.07); height: 100%; text-align: center;'>
<div class="result-glowing-box">
<div style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-bottom: 0.75rem;">Predicted Valuation</div>
<div class="result-price">${prediction:,.2f}</div>
<p style="color: #9ca3af; font-size: 0.85rem; margin-top: 1rem;">
Based on the Random Forest model trained on California Housing.
</p>
<div style="margin-top: 1.5rem; text-align: left; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 1rem; border: 1px solid rgba(255,255,255,0.05);">
<div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #6366f1; margin-bottom: 0.5rem;">Input Signature</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.75rem; color: #9ca3af;">
<div>Coord: <strong style="color: white;">{latitude}, {longitude}</strong></div>
<div>Income: <strong style="color: white;">${int(median_income*10000):,}</strong></div>
<div>Age: <strong style="color: white;">{housing_median_age} Yrs</strong></div>
<div>Rooms: <strong style="color: white;">{total_rooms:,}</strong></div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.error("Model or pipeline not loaded correctly.")
        else:
            st.markdown("""
<div style='background: rgba(17, 25, 40, 0.65); padding: 2rem; border-radius: 20px; border: 1px solid rgba(255,255,255,0.07); height: 100%; text-align: center;'>
<div style="padding: 2rem 1rem; margin-top: 2rem;">
<h3 style="font-family: 'Outfit'; font-size: 1.6rem; font-weight: 700; color: #f3f4f6; margin-bottom: 0.75rem;">Valuation Engine Ready</h3>
<p style="color: #9ca3af; font-size: 0.95rem; line-height: 1.5; margin-bottom: 2rem;">
Configure the local geographic coordinates and housing parameters using the control panel on the left, then trigger the predictive model.
</p>
<div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 14px; padding: 1.25rem; text-align: left;">
<h4 style="font-family: 'Outfit'; font-size: 0.95rem; font-weight: 600; color: #6366f1; margin-bottom: 0.5rem;">
Machine Learning Pipeline
</h4>
<p style="font-size: 0.8rem; color: #9ca3af; line-height: 1.45;">
Your inputs will be standardized and scaled using scikit-learn standard scaling, and categorical variables will be one-hot encoded before running random forest regression.
</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)
