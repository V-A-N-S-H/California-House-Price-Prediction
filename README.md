# 🏠 Housing Price Prediction using Machine Learning

This project implements a machine learning pipeline to predict housing prices using the California housing dataset. It includes data preprocessing, feature engineering, and a Random Forest model.

---

## 🚀 Features

- Data preprocessing using pipelines  
- Handling missing values  
- Feature scaling and encoding  
- Stratified sampling for balanced data  
- Random Forest Regression model  
- Model saving and loading using joblib  
- Prediction on new input data  

---

## 🛠️ Technologies Used

- Python  
- NumPy  
- Pandas  
- Scikit-learn  
- Joblib  

---

## 📂 Project Structure

├── main.py              # Main script for training and inference  
├── housing.csv          # Dataset  
├── input_data.csv       # Test input data  
├── output_data.csv      # Prediction output  
├── model.pkl            # Saved trained model  
├── pipeline.pkl         # Saved preprocessing pipeline  

---

## ⚙️ How It Works

1. Data Loading  
   Loads dataset from `housing.csv`  

2. Data Preprocessing  
   - Handles missing values using median  
   - Scales numerical features  
   - Encodes categorical features using OneHotEncoder  

3. Stratified Sampling  
   Splits dataset based on income category for better distribution  

4. Model Training  
   Uses RandomForestRegressor to train the model  

5. Model Saving  
   Saves trained model as `model.pkl` and pipeline as `pipeline.pkl`  

---

## 🔁 Training Mode

If model file does not exist, run:

python main.py

The model will be trained and saved.

---

## 🔮 Prediction Mode

If model already exists:
- Loads model and pipeline  
- Reads input from `input_data.csv`  
- Generates predictions  
- Saves output to `output_data.csv`  

---

## 📊 Output

Predicted values are stored in a column named:

median_house_value

---

## 💡 Example Workflow

1. Run script first time → Model trains  
2. Run again → Predictions generated  
3. Check `output_data.csv` for results  

---

## 🎯 Future Improvements

- Add hyperparameter tuning  
- Use advanced models like XGBoost  
- Add visualization dashboard  
- Deploy as web app using Flask or Streamlit  

---

## 👨‍💻 Author

Vansh Kashyap  

---

## ⭐ Note

This project is suitable for:
- Machine Learning beginners  
- Data Science projects  
- College mini-project submissions  
