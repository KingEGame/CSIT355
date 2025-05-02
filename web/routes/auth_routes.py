from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import db, Student, Professor, StudentStatus, ProfessorStatus
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from ..forms import LoginForm
import re

auth = Blueprint('auth', __name__)

def sanitize_user_id(user_id):
    return user_id.isalnum()

@auth.route('/')
def index():
    if current_user.is_authenticated:
        if session.get('user_type') == 'student':
            return redirect(url_for('students.dashboard'))
        elif session.get('user_type') == 'professor':
            return redirect(url_for('professors.dashboard'))
        elif session.get('user_type') == 'admin':
            return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        user_type = form.user_type.data

        if not sanitize_user_id(user_id):
            flash('Invalid user ID format', 'error')
            return redirect(url_for('auth.login'))

        if user_type == 'student':
            student = Student.query.get(user_id)
            if not student:
                flash('Student not found', 'error')
                return redirect(url_for('auth.login'))

            if student.status != StudentStatus.active:
                flash('Student account is not active', 'error')
                return redirect(url_for('auth.login'))

            login_user(student)
            session['user_type'] = 'student'
            session['student_id'] = student.student_id  # Add student_id to session
            print(f"Session after student login: {session}")  # Debug log
            return redirect(url_for('students.dashboard'))

        elif user_type == 'professor':
            professor = Professor.query.get(user_id)
            if not professor:
                flash('Professor not found', 'error')
                return redirect(url_for('auth.login'))

            if professor.status != ProfessorStatus.active:
                flash('Professor account is not active', 'error')
                return redirect(url_for('auth.login'))

            login_user(professor)
            session['user_type'] = 'professor'
            session['professor_id'] = professor.professor_id  # Add professor_id to session
            print(f"Session after professor login: {session}")  # Debug log
            return redirect(url_for('professors.dashboard'))

        elif user_type == 'admin':
            if user_id == 'admin':
                session['user_type'] = 'admin'
                return redirect(url_for('admin.dashboard'))
            flash('Invalid admin credentials', 'error')

        else:
            flash('Invalid user type', 'error')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index.html'))

def generate_next_student_id():
    last_student = Student.query.order_by(Student.student_id.desc()).first()
    if last_student and re.match(r"ST\\d{3,}", last_student.student_id):
        last_num = int(last_student.student_id[2:])
        next_num = last_num + 1
    else:
        next_num = 1
    return f"ST{next_num:03d}"

@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        try:
            new_student_id = generate_next_student_id()
            student = Student(
                student_id=new_student_id,
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

def generate_next_professor_id():
    last_prof = Professor.query.order_by(Professor.professor_id.desc()).first()
    if last_prof and re.match(r"PR\\d{3,}", last_prof.professor_id):
        last_num = int(last_prof.professor_id[2:])
        next_num = last_num + 1
    else:
        next_num = 1
    return f"PR{next_num:03d}"

@auth.route('/register/professor', methods=['GET', 'POST'])
def register_professor():
    if request.method == 'POST':
        try:
            new_professor_id = generate_next_professor_id()
            professor = Professor(
                professor_id=new_professor_id,
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