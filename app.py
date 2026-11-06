import sqlite3
import joblib
import numpy as np
from datetime import date
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'smart_meal_super_secret_key_786'
DB_NAME = 'mess.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meal_date DATE NOT NULL,
            meal_type TEXT NOT NULL,
            status TEXT NOT NULL,
            special_opted INTEGER DEFAULT 0,
            UNIQUE(user_id, meal_date, meal_type)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL,
            meal_type INTEGER NOT NULL,
            special_item INTEGER DEFAULT 0,
            is_weekend INTEGER DEFAULT 0,
            expected_students INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()
model = joblib.load('food_model.pkl')

# --- PAGE ROUTES ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('student_page'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('student_page'))
    return render_template('login.html')

@app.route('/student')
def student_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('student.html')

@app.route('/prediction')
def prediction_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('prediction.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- AUTH APIS ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    roll_no = data.get('roll_no')
    password = data.get('password')

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, roll_no, password) VALUES (?, ?, ?)", (name, roll_no, password))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Account created! Please login."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Roll number already registered!"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    roll_no = data.get('roll_no')
    password = data.get('password')

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE roll_no = ? AND password = ?", (roll_no, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['roll_no'] = user['roll_no']
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid Roll No or Password"}), 401

# --- ATTENDANCE API ---
@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Please login first"}), 401

    data = request.get_json()
    user_id = session['user_id']
    meal_date = data.get('meal_date')
    meal_idx = data.get('meal_type_idx')
    meal_types = ['Breakfast', 'Lunch', 'Dinner']
    chosen_meal = meal_types[meal_idx]
    status = data.get('status')
    special_opted = data.get('special_opted', 0)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_attendance (user_id, meal_date, meal_type, status, special_opted)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, meal_date, meal_type) DO UPDATE SET
            status=excluded.status,
            special_opted=excluded.special_opted
    ''', (user_id, meal_date, chosen_meal, status, special_opted))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Attendance recorded!"})

# --- PREDICTION API ---
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    day_of_week = int(data.get('day_of_week', 1))
    meal_type_idx = int(data.get('meal_type', 1))
    special_item = int(data.get('special_item', 0))
    is_weekend = 1 if day_of_week in [5, 6] else 0

    features = np.array([[day_of_week, meal_type_idx, special_item, is_weekend]])
    ai_predicted = int(round(model.predict(features)[0]))

    meal_names = ['Breakfast', 'Lunch', 'Dinner']
    chosen_meal = meal_names[meal_type_idx]
    today_str = str(date.today())

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN status='Eating' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END)
        FROM student_attendance 
        WHERE meal_date = ? AND meal_type = ?
    ''', (today_str, chosen_meal))
    eating_cnt, absent_cnt = cursor.fetchone()
    conn.close()

    eating_cnt = eating_cnt or 0
    absent_cnt = absent_cnt or 0

    final_count = max(eating_cnt, ai_predicted - absent_cnt)

    return jsonify({
        "status": "success",
        "ai_prediction": ai_predicted,
        "confirmed_eating": eating_cnt,
        "confirmed_absent": absent_cnt,
        "final_requirement_headcount": final_count,
        "food_plan": {
            "rice_kg": round(final_count * 0.08, 1),
            "dal_ltr": round(final_count * 0.12, 1),
            "roti_pcs": int(final_count * 3.2)
        }
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT meal_type, AVG(expected_students) as avg_students
        FROM meal_records
        GROUP BY meal_type
    ''')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)