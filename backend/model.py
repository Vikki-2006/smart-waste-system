import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

import tempfile
MODEL_PATH = os.path.join(tempfile.gettempdir(), 'rf_model.pkl')

def train_model(data_path):
    if not os.path.exists(data_path):
        print(f"Data file {data_path} not found. Returning.")
        return False
        
    df = pd.read_csv(data_path)
    # Feature Engineering
    # We predict if fill_level > 80% (1) or not (0) 
    # For a real system we would use historical fill levels and time.
    # Here we simulate by adding some noise to current fill level and creating a target feature.
    np.random.seed(42)
    # Target: 1 if it will overflow in the next cycle, 0 otherwise
    df['target'] = (df['fill_level'] + np.random.normal(5, 10, len(df)) > 80).astype(int)
    
    # Features: current fill_level, bin_id (as proxy for location specific patterns)
    X = df[['bin_id', 'fill_level']]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model trained with accuracy: {accuracy:.2f}")
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
        
    return True

def predict_overflow(bin_id, fill_level):
    if not os.path.exists(MODEL_PATH):
        # Fallback if no model is trained
        return int(fill_level > 75)
        
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
        
    # Model expects 2D array: bin_id, fill_level
    prediction = model.predict([[bin_id, fill_level]])
    return int(prediction[0])

if __name__ == '__main__':
    # Try training if script run directly
    train_model('../dataset/waste_data.csv')
