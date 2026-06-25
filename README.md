# California House Price Prediction

A Machine Learning project that predicts California house prices using housing features such as location, median income, population, total rooms, total bedrooms, and ocean proximity. The application is built with Streamlit and uses a Random Forest Regression model to provide accurate house price predictions along with an interactive analytics dashboard.

## Live Demo

Deployment:
https://california-house-price-prediction-ecuopu6vyxc66tjbdr2bhn.streamlit.app/

---

## Features

* Predict California house prices using machine learning
* Interactive dashboard for housing data analysis
* Geographic visualization of housing data
* Random Forest Regression model
* Data preprocessing using Scikit-learn Pipeline
* Interactive Streamlit user interface
* Fast and accurate predictions

---

## Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* Scikit-learn
* Joblib
* Streamlit ECharts

---

## Project Structure

```text
California-House-Price-Prediction/
│
├── streamlit_app.py        # Streamlit application
├── main.py                 # Model training script
├── housing.csv             # California housing dataset
├── input_data.csv          # Sample input data
├── output_data.csv         # Prediction output
├── model.pkl               # Trained Random Forest model
├── pipeline.pkl            # Data preprocessing pipeline
├── requirements.txt        # Project dependencies
├── README.md
└── .gitignore
```

---

## How It Works

1. Load the California Housing dataset.
2. Create a stratified train-test split.
3. Handle missing values using SimpleImputer.
4. Scale numerical features using StandardScaler.
5. Encode categorical features using OneHotEncoder.
6. Train a Random Forest Regression model.
7. Save the trained model and preprocessing pipeline.
8. Accept user input through the Streamlit interface.
9. Predict the estimated house price instantly.

---

## Dataset

The project uses the California Housing Dataset containing housing information such as:

* Longitude
* Latitude
* Housing Median Age
* Total Rooms
* Total Bedrooms
* Population
* Households
* Median Income
* Ocean Proximity
* Median House Value

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/V-A-N-S-H/California-House-Price-Prediction.git
```

### 2. Navigate to the project directory

```bash
cd California-House-Price-Prediction
```

### 3. Install the required dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run streamlit_app.py
```

---

## Machine Learning Workflow

* Data Cleaning
* Stratified Train-Test Split
* Missing Value Imputation
* Feature Scaling
* One-Hot Encoding
* Random Forest Regression
* Model Evaluation
* House Price Prediction

---

## Model Used

* Random Forest Regressor

---

## Input Features

The model predicts house prices using the following features:

* Longitude
* Latitude
* Housing Median Age
* Total Rooms
* Total Bedrooms
* Population
* Households
* Median Income
* Ocean Proximity

---

## Future Improvements

* Compare multiple regression models
* Hyperparameter tuning
* Feature importance visualization
* Real-time data integration
* Batch prediction using CSV upload
* Model performance dashboard

---

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## Author

**Vansh**

GitHub: https://github.com/V-A-N-S-H

---

## Support

If you found this project helpful, consider giving it a star on GitHub.
