import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

np.random.seed(42)
records = []

for _ in range(1200):
    day = np.random.randint(0, 7)
    meal = np.random.randint(0, 3)  # 0: Breakfast, 1: Lunch, 2: Dinner
    special = 1 if np.random.rand() > 0.75 else 0
    is_weekend = 1 if day in [5, 6] else 0
    
    base = 230 if meal == 1 else (210 if meal == 2 else 160)
    if is_weekend:
        base -= 50
    if special:
        base += 40
        
    students = int(base + np.random.normal(0, 10))
    records.append([day, meal, special, is_weekend, max(40, students)])

df = pd.DataFrame(records, columns=['day_of_week', 'meal_type', 'special_item', 'is_weekend', 'expected_students'])
X = df[['day_of_week', 'meal_type', 'special_item', 'is_weekend']]
y = df['expected_students']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, 'food_model.pkl')
print("Model train ho gaya aur 'food_model.pkl' ban chuki hai!")