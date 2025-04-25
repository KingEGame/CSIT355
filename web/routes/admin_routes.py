from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Course, Professor, Schedule, Teaching, CourseLevel, Semester
from datetime import datetime

admin = Blueprint('admin', __name__)

def is_admin():
    return session.get('user_type') == 'admin'

@admin.before_request
def require_admin():
    if not is_admin():
        flash('Admin access required', 'error')
        return redirect(url_for('auth.login'))

@admin.route('/admin/dashboard')
def dashboard():
    courses = Course.query.all()
    professors = Professor.query.all()
    schedules = Schedule.query.all()
    return render_template('admin/dashboard.html',
                         courses=courses,
                         professors=professors,
                         schedules=schedules)

@admin.route('/admin/courses')
def list_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin.route('/admin/course/new', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        try:
            course = Course(
                course_id=request.form['course_id'],
                course_code=request.form['course_code'],
                course_name=request.form['course_name'],
                description=request.form['description'],
                credits=int(request.form['credits']),
                department=request.form['department'],
                level=CourseLevel[request.form['level']],
                max_capacity=int(request.form['max_capacity'])
            )
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully', 'success')
            return redirect(url_for('admin.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating course: {str(e)}', 'error')
    
    return render_template('admin/course_form.html', course=None)

@admin.route('/admin/course/<course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        try:
            course.course_code = request.form['course_code']
            course.course_name = request.form['course_name']
            course.description = request.form['description']
            course.credits = int(request.form['credits'])
            course.department = request.form['department']
            course.level = CourseLevel[request.form['level']]
            course.max_capacity = int(request.form['max_capacity'])
            
            db.session.commit()
            flash('Course updated successfully', 'success')
            return redirect(url_for('admin.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'error')
    
    return render_template('admin/course_form.html', course=course)

@admin.route('/admin/schedule/new', methods=['GET', 'POST'])
def create_schedule():
    if request.method == 'POST':
        try:
            schedule = Schedule(
                schedule_id=request.form['schedule_id'],
                course_id=request.form['course_id'],
                semester=Semester[request.form['semester']],
                start_time=datetime.strptime(request.form['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(request.form['end_time'], '%H:%M').time(),
                meeting_days=request.form['meeting_days'],
                room_number=request.form['room_number']
            )
            db.session.add(schedule)
            db.session.commit()
            flash('Schedule created successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating schedule: {str(e)}', 'error')
    
    courses = Course.query.all()
    return render_template('admin/schedule_form.html',
                         schedule=None,
                         courses=courses)

@admin.route('/admin/teaching/assign', methods=['GET', 'POST'])
def assign_teaching():
    if request.method == 'POST':
        try:
            teaching = Teaching(
                teaching_id=request.form['teaching_id'],
                professor_id=request.form['professor_id'],
                schedule_id=request.form['schedule_id']
            )
            db.session.add(teaching)
            db.session.commit()
            flash('Professor assigned successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error assigning professor: {str(e)}', 'error')
    
    professors = Professor.query.all()
    schedules = Schedule.query.all()
    return render_template('admin/teaching_form.html',
                         professors=professors,
                         schedules=schedules)

@admin.route('/admin/teaching/remove', methods=['POST'])
def remove_teaching():
    teaching_id = request.form.get('teaching_id')
    try:
        teaching = Teaching.query.get(teaching_id)
        if teaching:
            db.session.delete(teaching)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Teaching assignment removed'})
        return jsonify({'success': False, 'message': 'Teaching assignment not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 