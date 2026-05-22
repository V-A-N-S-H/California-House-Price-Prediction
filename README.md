# California Housing Price Prediction

A Machine Learning project that predicts California housing prices using different housing features like income, population, total rooms, location, and ocean proximity.

This project uses a complete Machine Learning pipeline with data preprocessing, feature engineering, model training, and prediction using Random Forest Regression.

---

# About The Project

I made this project to learn:
- Machine Learning pipelines
- Data preprocessing
- Feature engineering
- Model training
- Flask web development
- Model deployment

The project can:
- Train a machine learning model
- Save the trained model
- Load the saved model
- Predict house prices using user input
- Provide predictions through a Flask web interface

---

# Technologies Used

- Python
- Flask
- NumPy
- Pandas
- Scikit-learn
- Joblib
- HTML
- CSS
- JavaScript

---

# Project Structure

```text
California-Housing-Price-Prediction/
│
├── static/                         # Static files
│   ├── css/                        # CSS files
│   ├── js/                         # JavaScript files
│
├── templates/                      # HTML templates
│   └── index.html
│
├── housing.csv                     # California housing dataset
├── input_data.csv                  # Input data for prediction
├── output_data.csv                 # Prediction output
│
├── model.pkl                       # Saved trained model
├── pipeline.pkl                    # Saved preprocessing pipeline
│
├── app.py                          # Flask web application
├── main.py                         # Model training and prediction script
├── requirements.txt                # Project dependencies
├── .gitignore
│
└── README.md                       # Project documentation
```

---

# Features

- Machine Learning pipeline
- Data preprocessing
- Missing value handling
- Feature scaling
- One-hot encoding
- Random Forest Regression model
- Model saving and loading
- Housing price prediction
- Flask web interface

---

# Machine Learning Workflow

1. Load California housing dataset  
2. Create stratified train-test split  
3. Handle missing values using SimpleImputer  
4. Scale numerical features using StandardScaler  
5. Encode categorical features using OneHotEncoder  
6. Train RandomForestRegressor model  
7. Save trained model and pipeline using Joblib  
8. Predict housing prices using new input data  

---

# Installation

## Step 1 — Clone the Repository

```bash
git clone <your-repository-link>
cd your-project-folder
```

---

## Step 2 — Install Requirements

```bash
pip install -r requirements.txt
```

---

# How To Run The Project

## Run Flask Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

# Input Features

The model predicts house prices using:

- Longitude
- Latitude
- Housing Median Age
- Total Rooms
- Total Bedrooms
- Population
- Households
- Median Income
- Ocean Proximity

---

# Model Used

- Random Forest Regressor

---

# Example Prediction

The user enters housing details in the web form, and the model predicts the estimated house price.

---

# Requirements

```text
flask
joblib
numpy
pandas
scikit-learn
```
