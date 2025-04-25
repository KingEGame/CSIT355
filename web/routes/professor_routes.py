from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Professor, Course, Schedule, Teaching, Enrolled, Grade
from datetime import datetime

professors_bp = Blueprint('professors', __name__)

@professors_bp.route('/dashboard')
def dashboard():
    if 'professor_id' not in session:
        return redirect(url_for('auth_bp.index'))
    professor = Professor.query.get(session['professor_id'])
    teaching_assignments = Teaching.query.filter_by(professor_id=session['professor_id']).all()
    return render_template('professors/dashboard.html', 
                         professor=professor, 
                         teaching_assignments=teaching_assignments)

@professors_bp.route('/courses')
def my_courses():
    if 'professor_id' not in session:
        return redirect(url_for('auth_bp.index'))
    teaching_assignments = Teaching.query.filter_by(professor_id=session['professor_id']).all()
    return render_template('professors/courses.html', teaching_assignments=teaching_assignments)

@professors_bp.route('/profile')
def profile():
    if 'professor_id' not in session:
        return redirect(url_for('auth_bp.index'))
    professor = Professor.query.get(session['professor_id'])
    return render_template('professors/profile.html', professor=professor)

@professors_bp.route('/professor/update-profile', methods=['POST'])
def update_profile():
    if 'professor_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    professor = Professor.query.get(session['professor_id'])
    if not professor:
        return jsonify({'success': False, 'message': 'Professor not found'})
    
    try:
        professor.first_name = request.form.get('first_name', professor.first_name)
        professor.last_name = request.form.get('last_name', professor.last_name)
        professor.department = request.form.get('department', professor.department)
        professor.email = request.form.get('email', professor.email)
        professor.office_number = request.form.get('office_number', professor.office_number)
        professor.phone = request.form.get('phone', professor.phone)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@professors_bp.route('/professor/course/<schedule_id>')
def course_details(schedule_id):
    if 'professor_id' not in session:
        return redirect(url_for('auth_bp.index'))
    
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        flash('Course schedule not found', 'error')
        return redirect(url_for('professors_bp.dashboard'))
    
    # Get enrolled students
    enrollments = Enrolled.query.filter_by(schedule_id=schedule_id).all()
    
    return render_template('professors/course_details.html',
                         schedule=schedule,
                         enrollments=enrollments)

@professors_bp.route('/professor/update-grade', methods=['POST'])
def update_grade():
    if 'professor_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    enrollment_id = request.form.get('enrollment_id')
    grade = request.form.get('grade')
    
    try:
        enrollment = Enrolled.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'success': False, 'message': 'Enrollment not found'})
        
        # Verify professor teaches this course
        teaching = Teaching.query.filter_by(
            professor_id=session['professor_id'],
            schedule_id=enrollment.schedule_id
        ).first()
        
        if not teaching:
            return jsonify({'success': False, 'message': 'Unauthorized to update this grade'})
        
        enrollment.grade = Grade[grade]
        db.session.commit()
        return jsonify({'success': True, 'message': 'Grade updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 