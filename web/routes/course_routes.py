from flask import render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Course, Schedule, Enrollment, Prerequisites
from datetime import datetime
from . import courses  # Ensure this line is present to import the courses blueprint

@courses.route('/dashboard')
def index():
    if 'student_id' not in session:
        return redirect(url_for('auth.index'))
    return render_template('dashboard.html', student_name=session['student_name'])

@courses.route('/courses')
def list_courses():
    if 'student_id' not in session:
        return redirect(url_for('auth.index'))
    schedules = Schedule.query.all()
    return render_template('courses.html', courses=schedules)

@courses.route('/my-courses')
def my_courses():
    if 'student_id' not in session:
        return redirect(url_for('auth.index'))
    enrollments = Enrollment.query.filter_by(student_id=session['student_id']).all()
    return render_template('my_courses.html', courses=enrollments)

@courses.route('/enroll', methods=['POST'])
def enroll():
    if 'student_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    schedule_id = request.form.get('schedule_id')
    try:
        enrollment = Enrollment(
            student_id=session['student_id'],
            schedule_id=schedule_id
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Successfully enrolled in the course!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@courses.route('/withdraw', methods=['POST'])
def withdraw():
    if 'student_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    schedule_id = request.form.get('schedule_id')
    try:
        enrollment = Enrollment.query.filter_by(
            student_id=session['student_id'],
            schedule_id=schedule_id
        ).first()
        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Successfully withdrawn from the course!'})
        return jsonify({'success': False, 'message': 'Enrollment not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@courses.route('/search')
def search():
    if 'student_id' not in session:
        return redirect(url_for('auth.index'))
    search_term = request.args.get('q', '')
    schedules = Schedule.query.join(Course).filter(
        (Course.course_id.like(f'%{search_term}%')) |
        (Course.course_name.like(f'%{search_term}%'))
    ).all()
    return render_template('search.html', courses=schedules, search_term=search_term)

@courses.route('/prerequisites/<course_id>')
def prerequisites(course_id):
    if 'student_id' not in session:
        return redirect(url_for('auth.index'))
    prerequisites = Prerequisites.query.filter_by(course_id=course_id).all()
    return render_template('prerequisites.html', prerequisites=prerequisites, course_id=course_id) 