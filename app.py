from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import numpy as np
import uuid

import db_manager
from auth import login_required, admin_required
import face_engine

app = Flask(__name__)
app.secret_key = 'super_secret_attendance_key_only_for_demo'

# Ensure directories exist
os.makedirs('static/students', exist_ok=True)
db_manager.init_db()

@app.context_processor
def inject_user():
    return dict(current_user=session.get('username'), current_role=session.get('role'))

# --- AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_manager.get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- DASHBOARD APP ROUTES ---
@app.route('/')
@login_required
def dashboard():
    stats = db_manager.get_stats()
    recent_attendance = db_manager.get_todays_attendance()[:5] # Last 5
    return render_template('dashboard.html', stats=stats, attendance=recent_attendance)

# --- STUDENT MANAGEMENT ---
@app.route('/students')
@login_required
def manage_students():
    students = db_manager.get_all_students()
    return render_template('manage_students.html', students=students)

@app.route('/students/add', methods=['GET'])
@login_required
def add_student_page():
    return render_template('add_student.html')

@app.route('/api/students/add', methods=['POST'])
@login_required
def api_add_student():
    data = request.json
    name = data.get('name')
    student_roll = data.get('student_roll')
    image_b64 = data.get('image_base64')
    
    if not all([name, student_roll, image_b64]):
        return jsonify({"success": False, "message": "Missing fields"}), 400
        
    img = face_engine.decode_base64_image(image_b64)
    encoding = face_engine.get_face_encoding(img)
    
    if encoding is None:
        return jsonify({"success": False, "message": "No face detected in the image"}), 400
        
    # Save Image to disk
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join('static', 'students', filename)
    import cv2
    cv2.imwrite(filepath, img)
    
    # Save to db
    success = db_manager.add_student(student_roll, name, filepath, encoding)
    if success:
        return jsonify({"success": True, "message": "Student registered successfully"})
    else:
        # Fallback if student_roll exists
        os.remove(filepath)
        return jsonify({"success": False, "message": "Student roll ID already exists"}), 400

@app.route('/api/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = db_manager.get_student_by_id(student_id)
    if student:
        try:
            os.remove(student['image_path'])
        except:
            pass
        db_manager.delete_student(student_id)
        flash('Student removed.', 'success')
    return redirect(url_for('manage_students'))

# --- ATTENDANCE SYSTEM ---
@app.route('/attendance/take')
@login_required
def take_attendance():
    return render_template('attendance.html')

@app.route('/attendance/view')
@login_required
def view_attendance():
    records = db_manager.get_todays_attendance()
    return render_template('view_attendance.html', records=records)

@app.route('/api/attendance/recognize', methods=['POST'])
@login_required
def api_recognize():
    data = request.json
    image_b64 = data.get('image_base64')
    if not image_b64:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    img = face_engine.decode_base64_image(image_b64)
    encoding = face_engine.get_face_encoding(img)
    
    if encoding is None:
        return jsonify({"success": False, "message": "No face found"}), 200
        
    # Load all students 
    students = db_manager.get_all_students()
    known_encodings = {}
    for s in students:
        if s['face_encoding']:
            known_encodings[s['id']] = np.array(json.loads(s['face_encoding']))
            
    match_id = face_engine.find_match(encoding, known_encodings)
    
    if match_id:
        student = db_manager.get_student_by_id(match_id)
        success, msg = db_manager.log_attendance(match_id)
        if success:
            return jsonify({
                "success": True, 
                "message": f"Welcome {student['name']}. Attendance marked.",
                "student_name": student['name']
            })
        else:
            return jsonify({"success": False, "message": msg, "student_name": student['name']})
            
    return jsonify({"success": False, "message": "Face not recognized"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
