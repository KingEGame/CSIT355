from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Student, StudentStatus, Schedule, Enrolled, EnrollmentStatus, Course, CourseLevel
from datetime import datetime
from flask_login import login_required, current_user

students = Blueprint('students', __name__)

@students.route('/student/profile')
def profile():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))
    
    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('student/profile.html', student=student)

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
    
    # Get current enrollments
    current_enrollments = student.enrollments
    
    return render_template('student/dashboard.html', 
                         student=student,
                         enrollments=current_enrollments)

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
    
    return render_template('student/academic_history.html',
                         student=student,
                         completed_courses=completed_courses)

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
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    schedule_id = request.form.get('schedule_id')
    
    try:
        student = Student.query.get(session['student_id'])
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        # Check if already enrolled
        existing_enrollment = Enrolled.query.filter_by(
            student_id=session['student_id'],
            schedule_id=schedule_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'success': False, 'message': 'Already enrolled in this course'})
        
        # Get course and schedule information
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'message': 'Course schedule not found'})
        
        course = Course.query.get(schedule.course_id)

        # Check if student has already completed this course
        completed_enrollment = Enrolled.query.join(Schedule).filter(
            Enrolled.student_id == session['student_id'],
            Schedule.course_id == course.course_id,
            Enrolled.status == EnrollmentStatus.completed
        ).first()
        
        if completed_enrollment:
            return jsonify({
                'success': False,
                'message': 'You have already completed this course and cannot take it again'
            })
        
        # Check course level restrictions
        allowed_levels = get_allowed_course_levels(student.level)
        if course.level not in allowed_levels:
            return jsonify({
                'success': False,
                'message': f'This course is not available for {student.level.value} students'
            })
        
        # Check credit limits
        if not check_credit_limits(student, course):
            return jsonify({
                'success': False,
                'message': 'Enrolling in this course would exceed your credit limit for the semester'
            })
        
        # Check course capacity
        if schedule.current_enrollment >= schedule.max_enrollment:
            return jsonify({'success': False, 'message': 'Course is full'})
        
        # Check prerequisites
        if course.prerequisites:
            # Get student's completed courses
            completed_courses = Enrolled.query.filter_by(
                student_id=session['student_id'],
                status=EnrollmentStatus.completed
            ).all()
            completed_course_ids = [e.schedule.course_id for e in completed_courses]
            
            # Check if all prerequisites are met
            for prereq in course.prerequisites:
                if prereq.prerequisite_course_id not in completed_course_ids:
                    prereq_course = Course.query.get(prereq.prerequisite_course_id)
                    return jsonify({
                        'success': False,
                        'message': f'Missing prerequisite: {prereq_course.course_code}'
                    })
        
        # Create new enrollment
        enrollment = Enrolled(
            student_id=session['student_id'],
            schedule_id=schedule_id,
            enrollment_date=datetime.utcnow(),
            status=EnrollmentStatus.enrolled
        )
        
        db.session.add(enrollment)
        
        # Update student's total credits for completed courses
        if student.total_credits is None:
            student.total_credits = 0
        student.total_credits += course.credits
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully registered for the course',
            'credits': course.credits,
            'total_credits': student.total_credits
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@students.route('/student/drop-course', methods=['POST'])
def drop_course():
    if 'student_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    enrollment_id = request.form.get('enrollment_id')
    
    try:
        enrollment = Enrolled.query.filter_by(
            enrollment_id=enrollment_id,
            student_id=session['student_id']
        ).first()
        
        if not enrollment:
            return jsonify({'success': False, 'message': 'Enrollment not found'})
        
        # Check if it's within the drop period (you can add your own logic here)
        if enrollment.status != EnrollmentStatus.enrolled:
            return jsonify({'success': False, 'message': 'Cannot drop this course at this time'})
        
        enrollment.status = EnrollmentStatus.dropped
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Successfully dropped the course'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

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