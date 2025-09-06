import json
import sqlite3
import os
from datetime import datetime
import bcrypt

def handler(event, context):
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Initialize database
        init_db()
        
        path = event['path'].split('/')[-1]
        method = event['httpMethod']
        
        if path == 'login' and method == 'POST':
            return handle_login(event, headers)
        elif path == 'register' and method == 'POST':
            return handle_register(event, headers)
        elif path == 'logout' and method == 'POST':
            return handle_logout(event, headers)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def init_db():
    conn = sqlite3.connect('/tmp/clearance_system.db')
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
    
    # Submitted clearances table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submitted_clearances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_name TEXT,
            student_number TEXT,
            completed_requirements TEXT,
            signature_template TEXT,
            submitted_date TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Insert single admin user
    admin_password = bcrypt.hashpw('ronron1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute('INSERT OR IGNORE INTO users (username, password, name, user_type) VALUES (?, ?, ?, ?)',
                  ('ronronadmin', admin_password, 'Ron', 'admin'))
    
    conn.commit()
    conn.close()

def handle_login(event, headers):
    data = json.loads(event['body'])
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('/tmp/clearance_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, name, user_type FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        session_data = {
            'user_id': user[0],
            'username': username,
            'name': user[2],
            'user_type': user[3]
        }
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'session': session_data,
                'redirect': 'admin_dashboard.html' if user[3] == 'admin' else 'student_dashboard.html'
            })
        }
    else:
        return {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
        }

def handle_register(event, headers):
    data = json.loads(event['body'])
    student_number = data.get('student_number')
    name = data.get('name')
    course = data.get('course')
    year = int(data.get('year'))
    major = data.get('major', '')
    section = data.get('section')
    
    conn = sqlite3.connect('/tmp/clearance_system.db')
    cursor = conn.cursor()
    
    # Check if student number already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (student_number,))
    if cursor.fetchone():
        conn.close()
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': 'Student number already registered'})
        }
    
    password_hash = bcrypt.hashpw(student_number.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute('INSERT INTO users (username, password, name, user_type, course, year, major, section) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (student_number, password_hash, name, 'student', course, year, major, section))
    conn.commit()
    conn.close()
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'success': True, 'message': 'Registration successful!'})
    }

def handle_logout(event, headers):
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'success': True})
    }