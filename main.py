import os
import joblib
import numpy as np    # for numerical operations
import pandas as pd   # for data analysis and manipulation
from sklearn.pipeline import Pipeline    # for creating a pipeline
from sklearn.impute import SimpleImputer    # for imputing missing values
from sklearn.compose import ColumnTransformer   # for creating a column transformer
from sklearn.model_selection import StratifiedShuffleSplit   # for splitting the data
from sklearn.preprocessing import StandardScaler, OneHotEncoder   # for feature scaling and encoding
from sklearn.ensemble import RandomForestRegressor   # for random forest regression



MODEL_FILE = "model.pkl"
PIPELINE = "pipeline.pkl"

def build_pipeline(num_attributes, cat_attributes):
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ('onehot', OneHotEncoder(handle_unknown='ignore')),  # ignore unknown values
    ])

    full_pipeline = ColumnTransformer([   
        ('num', num_pipeline, num_attributes), 
        ('cat', cat_pipeline, cat_attributes)
    ])

    return full_pipeline

if not os.path.exists(MODEL_FILE):
    # lets train the model

    # 1. Load the dataset 
    housing = pd.read_csv('housing.csv')

    # 2. Creating a stratified dataset
    housing.columns = housing.columns.str.strip()

    housing['income_cat'] = pd.cut(
        housing['median_income'],
        bins=[0., 1.5, 3.0, 4.5, 6., np.inf],
        labels=[1, 2, 3, 4, 5]
    )

    # 3. Spliting the dataset into train and test sets
    split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, test_index in split.split(housing, housing['income_cat']):
        strat_train_set = housing.iloc[train_index].drop('income_cat', axis=1)
        strat_test_set = housing.iloc[test_index].drop('income_cat', axis=1).to_csv('input_data.csv', index = False)

    # Now use strat_train_set for training
    housing = strat_train_set.copy()


    # 6. Seperating the featurs and labels
    housing_features = housing.drop('median_house_value', axis=1)  # features
    housing_labels = housing['median_house_value'].copy()  # labels

    # 7. Seperating the numerical and categorical features
    num_attributes = housing_features.drop('ocean_proximity', axis=1).columns.tolist()
    cat_attributes = ['ocean_proximity']

    # 11. Applying the pipeline to the training set and transforming the data
    pipeline = build_pipeline(num_attributes, cat_attributes) 
    housing_prepared = pipeline.fit_transform(housing_features)

    # 14. Train a random forest regression model
    model = RandomForestRegressor(random_state=42)
    model.fit(housing_prepared, housing_labels)

    # 15. Saving the model
    joblib.dump(model, MODEL_FILE)
    joblib.dump(pipeline, PIPELINE)
    print("Model is trained. Congrats!")

else:
    # lets load the model
    model = joblib.load(MODEL_FILE)
    pipeline = joblib.load(PIPELINE)
    
    input_data = pd.read_csv('input_data.csv')
    transformed_input = pipeline.transform(input_data)
    prediction = model.predict(transformed_input)
    input_data['median_house_value'] = prediction

    input_data.to_csv('output_data.csv', index=False)
    print("Inference is done. result is saved ot output.csv. Congrats!")
    






