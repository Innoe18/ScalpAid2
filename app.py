from flask import (
    Flask, flash, redirect, render_template,
    request, jsonify, abort, url_for
)
from flask import session

from database import SessionLocal, SensorReading, User, init_db
from config import API_KEY
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG, SECRET_KEY
import mysql.connector

app = Flask(__name__)
app.secret_key = SECRET_KEY
init_db()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, hair_type, purpose, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['name'], request.form['email'],
                  request.form['hair_type'], request.form['purpose'],
                  hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Registration successful!", "success")
            return redirect(url_for('register'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")

    return render_template('register.html')


def require_api_key():
    if request.headers.get("X-API-KEY") != API_KEY:
        abort(403, "Forbidden: Invalid API Key")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('profile'))
            else:
                flash("Invalid email or password.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")

    return render_template('login.html')
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, email, hair_type, purpose FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('home'))

        # Placeholder sensor data
        sensor_data = {
            "scalp_moisture": 0,
            "scalp_temperature": 0,
            "hair_strength": 0
        }

        # TODO: Replace zeros with real sensor data when connected
        return render_template('profile.html', user=user, sensor_data=sensor_data)

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('layout.html')


if __name__ == '__main__':
    app.run(debug=True)




