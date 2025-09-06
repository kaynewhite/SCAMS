from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'clearance_system_secret_key_2025'

# Database setup
def init_db():
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            user_type TEXT NOT NULL,
            course TEXT,
            year INTEGER,
            major TEXT,
            section TEXT
        )
    ''')
    
    # Requirements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Student requirements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            requirement_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (requirement_id) REFERENCES requirements (id)
        )
    ''')
    
    # Clearance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clearances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            submitted BOOLEAN DEFAULT FALSE,
            signature_template TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Insert default users
    admin_users = [
        ('admin1', 'admin123', 'Admin One', 'admin'),
        ('admin2', 'admin123', 'Admin Two', 'admin'),
        ('admin3', 'admin123', 'Admin Three', 'admin')
    ]
    
    student_users = [
        ('0221-1001', 'student123', 'John Doe', 'student', 'IT', 3, 'WMAD', 'A'),
        ('0222-1002', 'student123', 'Jane Smith', 'student', 'CS', 2, '', 'B')
    ]
    
    for username, password, name, user_type in admin_users:
        cursor.execute('INSERT OR IGNORE INTO users (username, password, name, user_type) VALUES (?, ?, ?, ?)',
                      (username, generate_password_hash(password), name, user_type))
    
    for username, password, name, user_type, course, year, major, section in student_users:
        cursor.execute('INSERT OR IGNORE INTO users (username, password, name, user_type, course, year, major, section) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                      (username, generate_password_hash(password), name, user_type, course, year, major, section))
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('clearance_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password, name, user_type FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['name'] = user[2]
            session['user_type'] = user[3]
            
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_number = request.form['student_number']
        name = request.form['name']
        course = request.form['course']
        year = int(request.form['year'])
        major = request.form.get('major', '')
        section = request.form['section']
        
        conn = sqlite3.connect('clearance_system.db')
        cursor = conn.cursor()
        
        # Check if student number already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (student_number,))
        if cursor.fetchone():
            flash('Student number already registered', 'error')
        else:
            cursor.execute('INSERT INTO users (username, password, name, user_type, course, year, major, section) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                          (student_number, generate_password_hash(student_number), name, 'student', course, year, major, section))
            conn.commit()
            flash('Registration successful! You can now login with your student number as password.', 'success')
            conn.close()
            return redirect(url_for('login'))
        
        conn.close()
    
    return render_template('register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)