from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import uuid
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
    cursor.execute('INSERT OR IGNORE INTO users (username, password, name, user_type) VALUES (?, ?, ?, ?)',
                  ('ronronadmin', generate_password_hash('ronron1234'), 'Ron', 'admin'))
    
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

# API Routes
@app.route('/api/requirements', methods=['GET', 'POST'])
def requirements_api():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        req_name = data.get('name', '').strip()
        
        if not req_name:
            return jsonify({'success': False, 'message': 'Requirement name is required'})
        
        try:
            cursor.execute('INSERT INTO requirements (name) VALUES (?)', (req_name,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Requirement added successfully'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Requirement already exists'})
        finally:
            conn.close()
    
    else:  # GET
        cursor.execute('SELECT id, name FROM requirements ORDER BY name')
        requirements = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(requirements)

@app.route('/api/students')
def students_api():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Get filter parameters
    student_number = request.args.get('student_number', '').strip()
    course = request.args.get('course', '').strip()
    year = request.args.get('year', '').strip()
    major = request.args.get('major', '').strip()
    section = request.args.get('section', '').strip()
    
    # Build query with filters
    query = '''
        SELECT u.id, u.username, u.name, u.course, u.year, u.major, u.section,
               CASE WHEN c.submitted IS NULL THEN 0 ELSE c.submitted END as clearance_submitted
        FROM users u
        LEFT JOIN clearances c ON u.id = c.student_id
        WHERE u.user_type = 'student'
    '''
    params = []
    
    if student_number:
        query += ' AND u.username LIKE ?'
        params.append(f'%{student_number}%')
    if course:
        query += ' AND u.course = ?'
        params.append(course)
    if year:
        query += ' AND u.year = ?'
        params.append(int(year))
    if major:
        query += ' AND u.major = ?'
        params.append(major)
    if section:
        query += ' AND u.section = ?'
        params.append(section)
    
    query += ' ORDER BY u.name'
    
    cursor.execute(query, params)
    students_data = cursor.fetchall()
    
    # Get all requirements
    cursor.execute('SELECT id, name FROM requirements ORDER BY name')
    requirements = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    # Get student requirements
    students = []
    for student_row in students_data:
        student_id = student_row[0]
        cursor.execute('''
            SELECT requirement_id, completed 
            FROM student_requirements 
            WHERE student_id = ?
        ''', (student_id,))
        
        student_reqs = cursor.fetchall()
        student_requirements = [{'requirement_id': row[0], 'completed': bool(row[1])} for row in student_reqs]
        
        students.append({
            'id': student_row[0],
            'username': student_row[1],
            'name': student_row[2],
            'course': student_row[3],
            'year': student_row[4],
            'major': student_row[5] or '',
            'section': student_row[6],
            'clearance_submitted': bool(student_row[7]),
            'requirements': student_requirements
        })
    
    conn.close()
    return jsonify({'students': students, 'requirements': requirements})

@app.route('/api/student-requirement', methods=['POST'])
def student_requirement_api():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    student_id = data.get('student_id')
    requirement_id = data.get('requirement_id')
    completed = data.get('completed', False)
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute('''
        SELECT id FROM student_requirements 
        WHERE student_id = ? AND requirement_id = ?
    ''', (student_id, requirement_id))
    
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE student_requirements 
            SET completed = ? 
            WHERE student_id = ? AND requirement_id = ?
        ''', (completed, student_id, requirement_id))
    else:
        cursor.execute('''
            INSERT INTO student_requirements (student_id, requirement_id, completed) 
            VALUES (?, ?, ?)
        ''', (student_id, requirement_id, completed))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/submit-clearance', methods=['POST'])
def submit_clearance_api():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    student_id = data.get('student_id')
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Check if student has completed all requirements
    cursor.execute('SELECT COUNT(*) FROM requirements')
    total_reqs = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM student_requirements 
        WHERE student_id = ? AND completed = 1
    ''', (student_id,))
    completed_reqs = cursor.fetchone()[0]
    
    if completed_reqs < total_reqs:
        conn.close()
        return jsonify({'success': False, 'message': 'Student has not completed all requirements'})
    
    # Get student info and completed requirements
    cursor.execute('SELECT username, name FROM users WHERE id = ?', (student_id,))
    student_info = cursor.fetchone()
    
    cursor.execute('''
        SELECT r.name 
        FROM requirements r
        JOIN student_requirements sr ON r.id = sr.requirement_id
        WHERE sr.student_id = ? AND sr.completed = 1
        ORDER BY r.name
    ''', (student_id,))
    
    completed_reqs = [row[0] for row in cursor.fetchall()]
    
    # Get signature template
    cursor.execute('SELECT signature_template FROM clearances WHERE student_id = ?', (student_id,))
    sig_template = cursor.fetchone()
    signature_template = sig_template[0] if sig_template else None
    
    # Move to submitted clearances table
    submitted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO submitted_clearances 
        (student_id, student_name, student_number, completed_requirements, signature_template, submitted_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, student_info[1], student_info[0], json.dumps(completed_reqs), signature_template, submitted_date))
    
    # Remove from active clearances
    cursor.execute('DELETE FROM clearances WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM student_requirements WHERE student_id = ?', (student_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/student-requirements')
def student_requirements_api():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({'success': False, 'message': 'Student access required'}), 403
    
    student_id = session['user_id']
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Get all requirements with student's completion status
    cursor.execute('''
        SELECT r.id, r.name,
               CASE WHEN sr.completed IS NULL THEN 0 ELSE sr.completed END as completed
        FROM requirements r
        LEFT JOIN student_requirements sr ON r.id = sr.requirement_id AND sr.student_id = ?
        ORDER BY r.name
    ''', (student_id,))
    
    requirements = []
    for row in cursor.fetchall():
        requirements.append({
            'id': row[0],
            'name': row[1],
            'completed': bool(row[2])
        })
    
    # Check clearance status
    cursor.execute('SELECT submitted FROM clearances WHERE student_id = ?', (student_id,))
    clearance_row = cursor.fetchone()
    clearance_submitted = bool(clearance_row[0]) if clearance_row else False
    
    conn.close()
    
    return jsonify({
        'requirements': requirements,
        'clearance_submitted': clearance_submitted
    })

@app.route('/api/student-clearance')
def student_clearance_api():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({'success': False, 'message': 'Student access required'}), 403
    
    student_id = session['user_id']
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Check if clearance is submitted
    cursor.execute('SELECT submitted, signature_template FROM clearances WHERE student_id = ?', (student_id,))
    clearance_row = cursor.fetchone()
    
    if not clearance_row or not clearance_row[0]:
        return jsonify({'clearance_submitted': False})
    
    # Get completed requirements
    cursor.execute('''
        SELECT r.name 
        FROM requirements r
        JOIN student_requirements sr ON r.id = sr.requirement_id
        WHERE sr.student_id = ? AND sr.completed = 1
        ORDER BY r.name
    ''', (student_id,))
    
    completed_requirements = [{'name': row[0]} for row in cursor.fetchall()]
    signature_template = clearance_row[1]
    
    conn.close()
    
    return jsonify({
        'clearance_submitted': True,
        'completed_requirements': completed_requirements,
        'signature_template': signature_template
    })

@app.route('/api/signature-template', methods=['POST'])
def signature_template_api():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    if 'signature' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['signature']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        import uuid
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join('static', 'uploads', filename)
        
        # Create uploads directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        file.save(file_path)
        
        # Store the file path in the database (you could store this globally or per semester)
        # For now, we'll update all clearance records to use this signature template
        conn = sqlite3.connect('clearance_system.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE clearances SET signature_template = ?', (f'/static/uploads/{filename}',))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'file_path': f'/static/uploads/{filename}'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'})

@app.route('/api/all-students')
def all_students_api():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, name, course, year, major, section
        FROM users 
        WHERE user_type = 'student'
        ORDER BY name
    ''')
    
    students = []
    for row in cursor.fetchall():
        students.append({
            'username': row[0],
            'name': row[1],
            'course': row[2],
            'year': row[3],
            'major': row[4] or '',
            'section': row[5]
        })
    
    conn.close()
    return jsonify(students)

@app.route('/api/clear-all-requirements', methods=['POST'])
def clear_all_requirements():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    try:
        # Clear all requirements
        cursor.execute('DELETE FROM requirements')
        
        # Clear all student requirements
        cursor.execute('DELETE FROM student_requirements')
        
        # Move submitted clearances back to pending by deleting from submitted table
        cursor.execute('DELETE FROM submitted_clearances')
        
        # Reset clearances table to not submitted
        cursor.execute('UPDATE clearances SET submitted = FALSE')
        
        conn.commit()
        return jsonify({'success': True, 'message': 'All requirements cleared and submissions reverted'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@app.route('/api/undo-submission', methods=['POST'])
def undo_submission():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'success': False, 'message': 'Student ID is required'})
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    try:
        # Remove from submitted clearances
        cursor.execute('DELETE FROM submitted_clearances WHERE student_id = ?', (student_id,))
        
        # Update clearances table to not submitted
        cursor.execute('UPDATE clearances SET submitted = FALSE WHERE student_id = ?', (student_id,))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Submission undone successfully'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@app.route('/download-all-clearances')
def download_all_clearances():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_name, student_number, submitted_date
        FROM submitted_clearances
        ORDER BY student_name
    ''')
    
    clearances = cursor.fetchall()
    conn.close()
    
    # Create CSV content
    csv_content = "Name,Student Number,Course,Year Level,Section,Major,Submitted Date\n"
    
    # Get detailed student info for each clearance
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    for clearance in clearances:
        student_number = clearance[1]
        cursor.execute('''
            SELECT name, username, course, year, section, major
            FROM users 
            WHERE username = ? AND user_type = 'student'
        ''', (student_number,))
        
        student_info = cursor.fetchone()
        if student_info:
            csv_content += f"{student_info[0]},{student_info[1]},{student_info[2]},{student_info[3]},{student_info[4]},{student_info[5] or ''},{clearance[2]}\n"
    
    conn.close()
    
    # Create response
    response = make_response(csv_content)
    response.headers["Content-Disposition"] = "attachment; filename=all_completed_clearances.csv"
    response.headers["Content-Type"] = "text/csv"
    
    return response

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API Routes for Delete Operations
@app.route('/api/requirements/<int:req_id>', methods=['DELETE'])
def delete_requirement_api(req_id):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    # Delete associated student requirements first
    cursor.execute('DELETE FROM student_requirements WHERE requirement_id = ?', (req_id,))
    # Delete the requirement
    cursor.execute('DELETE FROM requirements WHERE id = ?', (req_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/submitted-clearances')
def submitted_clearances_api():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, student_name, student_number, submitted_date 
        FROM submitted_clearances 
        ORDER BY submitted_date DESC
    ''')
    
    clearances = []
    for row in cursor.fetchall():
        clearances.append({
            'id': row[0],
            'student_name': row[1],
            'student_number': row[2],
            'submitted_date': row[3]
        })
    
    conn.close()
    return jsonify(clearances)

@app.route('/api/download-clearance/<int:clearance_id>')
def download_clearance_api(clearance_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    conn = sqlite3.connect('clearance_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_name, student_number, completed_requirements, signature_template, submitted_date
        FROM submitted_clearances WHERE id = ?
    ''', (clearance_id,))
    
    clearance = cursor.fetchone()
    conn.close()
    
    if not clearance:
        return jsonify({'success': False, 'message': 'Clearance not found'}), 404
    
    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT,
    )
    
    story = []
    
    # Title
    story.append(Paragraph("STUDENT CLEARANCE CERTIFICATE", title_style))
    story.append(Spacer(1, 12))
    
    # Student Info
    story.append(Paragraph(f"<b>Student Name:</b> {clearance[0]}", normal_style))
    story.append(Paragraph(f"<b>Student Number:</b> {clearance[1]}", normal_style))
    story.append(Paragraph(f"<b>Date of Submission:</b> {clearance[4]}", normal_style))
    story.append(Spacer(1, 20))
    
    # Requirements
    story.append(Paragraph("<b>Completed Requirements:</b>", normal_style))
    story.append(Spacer(1, 12))
    
    requirements = json.loads(clearance[2])
    for req in requirements:
        story.append(Paragraph(f"• {req}", normal_style))
    
    story.append(Spacer(1, 30))
    
    # Signature section
    if clearance[3]:
        story.append(Paragraph("<b>Authorized Signatures:</b>", normal_style))
        story.append(Spacer(1, 12))
        # You would add the signature image here if needed
        story.append(Paragraph("[Signature Template Section]", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"clearance_{clearance[1]}_{clearance[4].replace(':', '_').replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)