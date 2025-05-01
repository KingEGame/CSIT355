from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import db, Student, Professor, StudentStatus, ProfessorStatus
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if 'student_id' in session:
        return redirect(url_for('students.dashboard'))
    elif 'professor_id' in session:
        return redirect(url_for('professors.dashboard'))
    return render_template('auth/login.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_type = request.form.get('user_type')
        
        if user_type == 'student':
            student = Student.query.get(user_id)
            if student and student.status == StudentStatus.active:
                session['student_id'] = student.student_id
                session['student_name'] = f"{student.first_name} {student.last_name}"
                session['user_type'] = 'student'
                return redirect(url_for('students.dashboard'))
            flash('Invalid student ID or inactive account', 'error')
        
        elif user_type == 'professor':
            professor = Professor.query.get(user_id)
            if professor and professor.status == ProfessorStatus.active:
                session['professor_id'] = professor.professor_id
                session['professor_name'] = f"{professor.first_name} {professor.last_name}"
                session['user_type'] = 'professor'
                return redirect(url_for('professors.dashboard'))
            flash('Invalid professor ID or inactive account', 'error')
        elif user_type == 'admin':
            if user_id == 'admin':
                session['user_type'] = 'admin'
                session['admin_name'] = 'Administrator'
                return redirect(url_for('admin.dashboard'))
            flash('Invalid admin credentials', 'error')
        
        else:
            flash('Invalid user type', 'error')
    
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))

# Registration routes can be added here if needed
@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        try:
            student = Student(
                student_id=request.form['student_id'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d'),
                major=request.form['major'],
                email=request.form['email'],
                enrollment_date=datetime.utcnow()
            )
            db.session.add(student)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('auth/register_student.html')

@auth.route('/register/professor', methods=['GET', 'POST'])
def register_professor():
    if request.method == 'POST':
        try:
            professor = Professor(
                professor_id=request.form['professor_id'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                department=request.form['department'],
                email=request.form['email'],
                office_number=request.form['office_number'],
                phone=request.form['phone'],
                hire_date=datetime.utcnow()
            )
            db.session.add(professor)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('auth/register_professor.html') 