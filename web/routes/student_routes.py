from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Student, StudentStatus, Schedule, Enrolled, EnrollmentStatus, Course, CourseLevel, Semester
from datetime import datetime
from flask_login import login_required, current_user
from ..forms import StudentForm

students = Blueprint('students', __name__)

@students.route('/student/profile')
def profile():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))

    # Initialize the form with student data
    form = StudentForm(obj=student)

    return render_template('student/profile.html', student=student, form=form)

@students.route('/student/update-profile', methods=['POST'])
def update_profile():
    if 'student_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    student = Student.query.get(session['student_id'])
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'})
    
    try:
        student.first_name = request.form.get('first_name', student.first_name)
        student.last_name = request.form.get('last_name', student.last_name)
        student.major = request.form.get('major', student.major)
        student.email = request.form.get('email', student.email)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@students.route('/student/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))

    # Get current enrollments excluding dropped courses
    current_enrollments = Enrolled.query.filter(
        Enrolled.student_id == session['student_id'],
        Enrolled.status == EnrollmentStatus.enrolled
    ).all()

    # Calculate completed credits
    completed_credits = sum(
        enrollment.schedule.course.credits
        for enrollment in student.enrollments
        if enrollment.status == EnrollmentStatus.completed
    )

    return render_template('student/dashboard.html', 
                           student=student, 
                           enrollments=current_enrollments, 
                           completed_credits=completed_credits)

@students.route('/student/academic-history')
def academic_history():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))
    
    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))
    
    # Get completed courses with grades
    completed_courses = [e for e in student.enrollments if e.grade is not None]

    # Calculate GPA
    grade_points = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'F': 0.0
    }
    total_points = sum(grade_points.get(e.grade, 0) * e.schedule.course.credits for e in completed_courses)
    total_credits = sum(e.schedule.course.credits for e in completed_courses)
    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    return render_template('student/academic_history.html',
                           student=student,
                           completed_courses=completed_courses,
                           gpa=gpa)

@students.route('/student/available-courses')
def available_courses():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))
    
    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))
    
    # Get courses appropriate for student's level
    allowed_levels = get_allowed_course_levels(student.level)
    
    # Get all available courses for the student's level
    schedules = Schedule.query.join(Course).filter(
        Schedule.current_enrollment < Schedule.max_enrollment,
        Course.level.in_(allowed_levels)
    ).all()
    
    # Get student's current enrollments to check for duplicates
    student_enrollments = Enrolled.query.filter_by(
        student_id=session['student_id']
    ).all()
    enrolled_schedule_ids = [e.schedule_id for e in student_enrollments]
    
    return render_template('student/available_courses.html',
                         schedules=schedules,
                         enrolled_schedule_ids=enrolled_schedule_ids,
                         student_level=student.level)

def get_allowed_course_levels(student_level):
    """Determine which course levels a student can take based on their academic level"""
    if student_level == CourseLevel.phd:
        return [CourseLevel.undergraduate, CourseLevel.graduate, CourseLevel.phd]
    elif student_level == CourseLevel.graduate:
        return [CourseLevel.undergraduate, CourseLevel.graduate]
    else:  # undergraduate
        return [CourseLevel.undergraduate]

def check_credit_limits(student, course):
    """Check if adding this course would exceed credit limits for the semester"""
    # Get current semester enrollments
    current_semester = get_current_semester()
    semester_enrollments = Enrolled.query.join(Schedule).filter(
        Enrolled.student_id == student.student_id,
        Enrolled.status == EnrollmentStatus.enrolled,
        Schedule.semester == current_semester
    ).all()
    
    # Calculate current semester credits
    current_credits = sum(e.schedule.course.credits for e in semester_enrollments)
    
    # Define credit limits based on student level
    if student.level == CourseLevel.undergraduate:
        max_credits = 18
    elif student.level == CourseLevel.graduate:
        max_credits = 12
    else:  # PhD
        max_credits = 9
    
    return current_credits + course.credits <= max_credits

def get_current_semester():
    """Determine the current semester based on the date"""
    month = datetime.utcnow().month
    if month >= 8 and month <= 12:
        return Semester.Fall
    elif month >= 1 and month <= 5:
        return Semester.Spring
    else:
        return Semester.Summer

@students.route('/student/register-course', methods=['POST'])
def register_course():
    if 'student_id' not in session:
        flash('You must be logged in to register for a course.', 'error')
        return redirect(url_for('auth.login'))

    schedule_id = request.form.get('schedule_id')

    try:
        student = Student.query.get(session['student_id'])
        if not student:
            flash('Student not found.', 'error')
            return redirect(url_for('students.available_courses'))

        # Check if already enrolled
        existing_enrollment = Enrolled.query.filter_by(
            student_id=session['student_id'],
            schedule_id=schedule_id
        ).first()

        if existing_enrollment:
            if existing_enrollment.status == EnrollmentStatus.dropped:
                # Allow re-registration by updating the status
                existing_enrollment.status = EnrollmentStatus.enrolled
                db.session.commit()
                flash('Successfully re-registered for the course.', 'success')
                return redirect(url_for('students.dashboard'))
            flash('You are already enrolled in this course.', 'error')
            return redirect(url_for('students.available_courses'))

        # Get course and schedule information
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            flash('Course schedule not found.', 'error')
            return redirect(url_for('students.available_courses'))

        # Create new enrollment
        enrollment = Enrolled(
            student_id=session['student_id'],
            schedule_id=schedule_id,
            enrollment_date=datetime.utcnow(),
            status=EnrollmentStatus.enrolled
        )

        db.session.add(enrollment)
        db.session.commit()

        flash('Course registered successfully.', 'success')
        return redirect(url_for('students.dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error registering for the course: {str(e)}', 'error')
        return redirect(url_for('students.available_courses'))

@students.route('/student/drop-course', methods=['POST'])
def drop_course():
    if 'student_id' not in session:
        flash('You must be logged in to drop a course.', 'error')
        return redirect(url_for('auth.login'))

    enrollment_id = request.form.get('enrollment_id')

    if not enrollment_id:
        flash('Enrollment ID is required to drop a course.', 'error')
        return redirect(url_for('students.dashboard'))

    try:
        enrollment = Enrolled.query.filter_by(
            enrollment_id=enrollment_id,
            student_id=session['student_id']
        ).first()

        if not enrollment:
            flash('Enrollment not found.', 'error')
            return redirect(url_for('students.dashboard'))

        # Check if it's within the drop period (you can add your own logic here)
        if enrollment.status != EnrollmentStatus.enrolled:
            flash('Cannot drop this course at this time.', 'error')
            return redirect(url_for('students.dashboard'))

        enrollment.status = EnrollmentStatus.dropped
        db.session.commit()

        flash('Course successfully dropped.', 'success')
        return redirect(url_for('students.dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error dropping the course: {str(e)}', 'error')
        return redirect(url_for('students.dashboard'))

@students.route('/check-level-upgrade')
@login_required
def check_level_upgrade():
    student = Student.query.get(current_user.id)
    
    if student.level.value == 'phd':
        return jsonify({
            'message': 'You are already at the highest academic level (PhD).'
        })
    
    can_upgrade = student.can_upgrade_level()
    current_gpa = student.get_gpa()
    completed_credits = student.get_completed_credits()
    
    if student.level.value == 'undergraduate':
        required_credits = 120
        required_gpa = 3.0
        next_level = 'graduate'
    else:  # graduate
        required_credits = 30
        required_gpa = 3.5
        next_level = 'phd'
    
    if can_upgrade and current_gpa >= required_gpa:
        message = f'Congratulations! You are eligible to upgrade to {next_level} level.<br><br>'
        message += f'Your GPA: {current_gpa:.2f} (Required: {required_gpa})<br>'
        message += f'Completed Credits: {completed_credits} (Required: {required_credits})'
    else:
        message = f'You are not yet eligible to upgrade to {next_level} level.<br><br>'
        message += f'Your GPA: {current_gpa:.2f} (Required: {required_gpa})<br>'
        message += f'Completed Credits: {completed_credits} (Required: {required_credits})'
    
    return jsonify({'message': message})

@students.route('/student/schedule')
def schedule():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))

    # Get current enrollments excluding dropped courses
    current_enrollments = Enrolled.query.filter_by(
        student_id=session['student_id'],
        status=EnrollmentStatus.enrolled
    ).all()

    return render_template('student/schedule.html', enrollments=current_enrollments)