from flask import render_template, request, redirect, url_for, flash, session
from ..models import db, Student
from datetime import datetime
from . import auth

@auth.route('/')
def index():
    if 'student_id' not in session:
        return render_template('login.html')
    return redirect(url_for('courses.index'))

@auth.route('/login', methods=['POST'])
def login():
    student_id = request.form.get('student_id')
    student = Student.query.get(student_id)
    if student:
        session['student_id'] = student_id
        session['student_name'] = f"{student.first_name} {student.last_name}"
        return redirect(url_for('courses.index'))
    flash('Invalid student ID', 'error')
    return redirect(url_for('auth.index'))

@auth.route('/register', methods=['POST'])
def register():
    student_id = request.form.get('student_id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
    major = request.form.get('major')

    student = Student(
        student_id=student_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        date_of_birth=date_of_birth,
        major=major
    )

    try:
        db.session.add(student)
        db.session.commit()
        session['student_id'] = student_id
        session['student_name'] = f"{first_name} {last_name}"
        flash('Registration successful!', 'success')
        return redirect(url_for('courses.index'))
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('auth.index'))

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index')) 