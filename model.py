import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
import joblib
import os

# Sample data for crop recommendation (typical dataset, since ICRISAT has no NPK-crop labels)
# Columns: N, P, K, temperature, humidity, ph, rainfall, label (crop)
crop_data = {
    'N': np.random.uniform(0, 140, 2000),
    'P': np.random.uniform(5, 145, 2000),
    'K': np.random.uniform(5, 205, 2000),
    'temperature': np.random.uniform(8, 43, 2000),
    'humidity': np.random.uniform(14, 100, 2000),
    'ph': np.random.uniform(2.5, 9.5, 2000),
    'rainfall': np.random.uniform(20, 300, 2000),
    'label': np.random.choice(['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'], 2000)
}

df = pd.DataFrame(crop_data)

# For real: load ICRISAT CSV, but no NPK; use this demo
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = pd.factorize(df['label'])[0]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    'XGBoost': XGBClassifier(random_state=42),
    'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
    'GradientBoosting': GradientBoostingClassifier(n_estimators=50, random_state=42),
    'NaiveBayes': GaussianNB(),
    'DecisionTree': DecisionTreeClassifier(random_state=42),
    'KNN': KNeighborsClassifier(n_neighbors=5)
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    prec = precision_score(y_test, y_pred, average='weighted')
    rec = recall_score(y_test, y_pred, average='weighted')
    print(f'\n{name} test metrics:')
    print(f'Accuracy: {acc*100:.1f}%')
    print(f'F1: {f1*100:.1f}%')
    print(f'Precision: {prec*100:.1f}%')
    print(f'Recall: {rec*100:.1f}%')
    print('\nClassification Report:\n', classification_report(y_test, y_pred))

# Save
joblib.dump(models['XGBoost'], 'crop_model.pkl')
joblib.dump(models['RandomForest'], 'rf_model.pkl')
joblib.dump(models['GradientBoosting'], 'gb_model.pkl')
joblib.dump(models['NaiveBayes'], 'nb_model.pkl')
joblib.dump(models['DecisionTree'], 'dt_model.pkl')
joblib.dump(models['KNN'], 'knn_model.pkl')
joblib.dump(df['label'].unique(), 'crop_labels.pkl')

print('Models saved')

