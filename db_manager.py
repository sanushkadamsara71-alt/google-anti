import sqlite3
import os
import json
from datetime import datetime

DB_NAME = 'database.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # Students Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_roll TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            image_path TEXT,
            face_encoding TEXT
        )
    ''')
    # Attendance Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Check if admin exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        from werkzeug.security import generate_password_hash
        default_pwd = generate_password_hash('admin123')
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                  ('admin', default_pwd, 'admin'))
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_student(student_roll, name, image_path, face_encoding):
    conn = get_connection()
    c = conn.cursor()
    encoding_json = json.dumps(face_encoding.tolist()) if face_encoding is not None else None
    try:
        c.execute("INSERT INTO students (student_roll, name, image_path, face_encoding) VALUES (?, ?, ?, ?)",
                  (student_roll, name, image_path, encoding_json))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_students():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return students
    
def get_student_by_id(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student= c.fetchone()
    conn.close()
    return student

def delete_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

def log_attendance(student_id):
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Check if already marked today
    c.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
    if c.fetchone():
        conn.close()
        return False, "Attendance already marked for today"
    
    c.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)",
              (student_id, today, current_time, "Present"))
    conn.commit()
    conn.close()
    return True, "Attendance marked successfully"

def get_todays_attendance():
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        SELECT a.*, s.name, s.student_roll 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.date=?
        ORDER BY a.time DESC
    ''', (today,))
    attendance = c.fetchall()
    conn.close()
    return attendance

def get_stats():
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    c.execute("SELECT COUNT(*) as count FROM students")
    total_students = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM attendance WHERE date=?", (today,))
    present_today = c.fetchone()['count']
    
    conn.close()
    return {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": total_students - present_today
    }
