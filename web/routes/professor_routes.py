from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Professor, Course, Schedule, Teaching, Enrolled, Grade
from datetime import datetime
from ..forms import ProfessorForm
from flask_login import current_user, login_required
import os
from werkzeug.utils import secure_filename

professors = Blueprint('professors', __name__)

@professors.route('/dashboard')
@login_required
def dashboard():
    professor = current_user

    # Fetch teaching assignments
    teaching_assignments = Teaching.query.filter_by(professor_id=professor.professor_id).all()

    # Calculate total courses
    total_courses = len(teaching_assignments)

    # Calculate total students
    total_students = sum(
        sum(1 for e in teaching.schedule.enrollments if e.status.name == 'enrolled')
        for teaching in teaching_assignments
    )

    total_course_load = sum(
        teaching.schedule.course.credits
        for teaching in teaching_assignments
    )
    # Determine the current semester
    current_semester = None
    if teaching_assignments:
        current_semester = teaching_assignments[0].schedule.semester

    # Fetch courses for the professor
    courses = [
        {
            "course_code": teaching.schedule.course.course_code,
            "course_name": teaching.schedule.course.course_name,
            "current_enrollment": sum(1 for e in teaching.schedule.enrollments if e.status.name == 'enrolled'),
            "max_capacity": teaching.schedule.course.max_capacity,
            "schedule_id": teaching.schedule.schedule_id,
        }
        for teaching in teaching_assignments
    ]

    return render_template(
        'professor/dashboard.html',
        current_user=professor,
        total_courses=total_courses,
        total_students=total_students,
        current_semester=current_semester,
        total_course_load=total_course_load,
        courses=courses
    )

@professors.route('/courses')
@login_required
def courses():
    professor = current_user
    teaching_assignments = Teaching.query.filter_by(professor_id=professor.professor_id).all()

    # Transform teaching assignments into courses list
    courses = [
        {
            "course": teaching.schedule.course,
            "materials": teaching.schedule.course.materials if hasattr(teaching.schedule.course, 'materials') else []
        }
        for teaching in teaching_assignments
    ]

    return render_template('professor/course_management.html', current_user=professor, courses=courses)

@professors.route('/courses')
def my_courses():
    if 'professor_id' not in session:
        return redirect(url_for('auth.index'))
    teaching_assignments = Teaching.query.filter_by(professor_id=session['professor_id']).all()
    return render_template('professors/courses.html', teaching_assignments=teaching_assignments)

@professors.route('/profile')
@login_required
def profile():
    professor = current_user

    if not professor:
        flash('Professor not found', 'error')
        return redirect(url_for('auth.index'))

    # Initialize the form with professor data
    form = ProfessorForm(obj=professor)

    return render_template('professor/profile.html', professor=professor, form=form)

@professors.route('/professor/update-profile', methods=['POST'])
@login_required
def update_profile():
    professor = current_user
    try:
        email = request.form.get('email', professor.email)
        existing_professor = Professor.query.filter_by(email=email).first()
        if existing_professor and existing_professor.professor_id != professor.professor_id:
            return jsonify({'success': False, 'message': 'Email already in use'})

        professor.first_name = request.form.get('first_name', professor.first_name)
        professor.last_name = request.form.get('last_name', professor.last_name)
        professor.department = request.form.get('department', professor.department)
        professor.email = email
        professor.office_number = request.form.get('office_number', professor.office_number)
        professor.phone = request.form.get('phone', professor.phone)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@professors.route('/professor/course/<schedule_id>')
def course_details(schedule_id):
    if 'professor_id' not in session:
        return redirect(url_for('auth.index'))
    
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        flash('Course schedule not found', 'error')
        return redirect(url_for('professors_bp.dashboard'))
    
    # Get enrolled students
    enrollments = Enrolled.query.filter_by(schedule_id=schedule_id).all()
    
    return render_template('professors/course_details.html',
                         schedule=schedule,
                         enrollments=enrollments)

@professors.route('/professor/update-grade', methods=['POST'])
@login_required
def update_grade():
    professor = current_user
    enrollment_id = request.form.get('enrollment_id')
    grade = request.form.get('grade')

    try:
        if grade not in Grade.__members__:
            return jsonify({'success': False, 'message': 'Invalid grade'})

        enrollment = Enrolled.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'success': False, 'message': 'Enrollment not found'})

        teaching = Teaching.query.filter_by(
            professor_id=professor.professor_id,
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

@professors.route('/schedule')
@login_required
def schedule():
    professor = current_user

    # Fetch teaching assignments and related schedule data
    teaching_assignments = Teaching.query.filter_by(professor_id=professor.professor_id).all()
    schedule_data = {}

    for teaching in teaching_assignments:
        schedule = teaching.schedule
        course = schedule.course

        # Parse meeting days and organize data
        for day in schedule.meeting_days:
            if day not in schedule_data:
                schedule_data[day] = []
            schedule_data[day].append({
                "course_code": course.course_code,
                "course_name": course.course_name,
                "start_time": schedule.start_time.strftime('%H:%M'),
                "end_time": schedule.end_time.strftime('%H:%M'),
                "room_number": schedule.room_number
            })

    return render_template('professor/schedule.html', current_user=professor, schedule_data=schedule_data)

@professors.route('/schedule/download')
@login_required
def download_schedule():
    professor = current_user

    # Fetch teaching assignments and related schedule data
    teaching_assignments = Teaching.query.filter_by(professor_id=professor.professor_id).all()
    schedule_data = []

    for teaching in teaching_assignments:
        schedule = teaching.schedule
        course = schedule.course

        # Parse meeting days and organize data
        for day in schedule.meeting_days:
            schedule_data.append({
                "day": day,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "start_time": schedule.start_time.strftime('%H:%M'),
                "end_time": schedule.end_time.strftime('%H:%M'),
                "room_number": schedule.room_number
            })

    # Generate a CSV file
    import csv
    from io import StringIO
    from flask import Response

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["day", "course_code", "course_name", "start_time", "end_time", "room_number"])
    writer.writeheader()
    writer.writerows(schedule_data)

    # Return the CSV file as a response
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=schedule.csv"})

# Removed the reference to `Material` in the `course_management` function.
@professors.route('/course-management')
@login_required
def course_management():
    professor = current_user
    teaching_assignments = Teaching.query.filter_by(professor_id=professor.professor_id).all()

    # Fetch courses dynamically without materials
    courses = [
        {
            "course": teaching.schedule.course
        }
        for teaching in teaching_assignments
    ]

    return render_template('professor/course_management.html', current_user=professor, courses=courses)

@professors.route('/course/<schedule_id>')
@login_required
def view_course(schedule_id):
    professor = current_user

    # Fetch the schedule details
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        flash('Schedule not found', 'error')
        return redirect(url_for('professors.dashboard'))

    # Ensure the professor is teaching this course
    teaching_assignment = Teaching.query.filter_by(professor_id=professor.professor_id, schedule_id=schedule_id).first()
    if not teaching_assignment:
        flash('You are not authorized to view this course', 'error')
        return redirect(url_for('professors.dashboard'))

    # Fetch enrolled students
    enrollments = Enrolled.query.filter_by(schedule_id=schedule_id, status='enrolled').all()

    return render_template('professor/course_details.html', schedule=schedule, enrollments=enrollments)

@professors.route('/add-course', methods=['GET', 'POST'])
@login_required
def add_course():
    professor = current_user

    if request.method == 'POST':
        course_code = request.form.get('course_code')
        course_name = request.form.get('course_name')
        description = request.form.get('description')
        credits = request.form.get('credits')

        if not course_code or not course_name or not credits:
            flash('All fields are required except description.', 'error')
            return redirect(url_for('professors.add_course'))

        try:
            new_course = Course(
                course_code=course_code,
                course_name=course_name,
                description=description,
                credits=int(credits),
                professor_id=professor.professor_id
            )
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully!', 'success')
            return redirect(url_for('professors.course_management'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {str(e)}', 'error')

    return render_template('professor/add_course.html', current_user=professor)