from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from web.models import Course, Schedule, Professor, Student, Enrolled, CourseLevel, Semester
from web.extensions import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from web.forms import ProfileForm

students = Blueprint('students', __name__)

@students.route('/dashboard')
@login_required
def dashboard():
    # Get current enrollments for the student
    current_enrollments = (Enrolled.query
        .filter_by(student_id=current_user.id)
        .join(Schedule)
        .join(Course)
        .all())
    
    # Calculate total credits
    total_credits = sum(enrollment.schedule.course.credits for enrollment in current_enrollments)
    
    return render_template('student/dashboard.html',
                         enrollments=current_enrollments,
                         total_credits=total_credits)

@students.route('/available-courses')
@login_required
def available_courses():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    semester = request.args.get('semester', 'all')
    level = request.args.get('level', 'all')
    
    # Base query
    query = (Schedule.query
        .join(Course)
        .join(Professor)
        .filter(Schedule.academic_year >= datetime.now().year))  # Only future or current year courses
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Course.course_code.ilike(search_term),
                Course.course_name.ilike(search_term)
            )
        )
    
    # Apply semester filter
    if semester != 'all':
        try:
            sem_enum = Semester[semester]
            query = query.filter(Schedule.semester == sem_enum)
        except KeyError:
            pass
    
    # Apply level filter
    if level != 'all':
        try:
            level_enum = CourseLevel[level]
            query = query.filter(Course.level == level_enum)
        except KeyError:
            pass
    
    # Get student's current enrollments to exclude
    enrolled_schedule_ids = db.session.query(Enrolled.schedule_id).filter_by(student_id=current_user.id)
    query = query.filter(~Schedule.schedule_id.in_(enrolled_schedule_ids))
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    courses = pagination.items
    
    return render_template('student/available_courses.html',
                         courses=courses,
                         pagination=pagination)

@students.route('/register-course', methods=['POST'])
@login_required
def register_course():
    schedule_id = request.form.get('schedule_id')
    if not schedule_id:
        flash('Invalid course selection.', 'error')
        return redirect(url_for('students.available_courses'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Check if already enrolled
    existing_enrollment = Enrolled.query.filter_by(
        student_id=current_user.id,
        schedule_id=schedule_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'error')
        return redirect(url_for('students.available_courses'))
    
    # Check if course is full
    if schedule.current_enrollment >= schedule.max_enrollment:
        flash('This course is full.', 'error')
        return redirect(url_for('students.available_courses'))
    
    # Create new enrollment
    enrollment = Enrolled(
        student_id=current_user.id,
        schedule_id=schedule_id,
        enrollment_date=datetime.now()
    )
    
    # Increment current enrollment
    schedule.current_enrollment += 1
    
    try:
        db.session.add(enrollment)
        db.session.commit()
        flash('Successfully registered for the course.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering for course: {str(e)}")
        flash('An error occurred while registering for the course.', 'error')
    
    return redirect(url_for('students.dashboard'))

@students.route('/drop-course', methods=['POST'])
@login_required
def drop_course():
    schedule_id = request.form.get('schedule_id')
    if not schedule_id:
        flash('Invalid course selection.', 'error')
        return redirect(url_for('students.dashboard'))
    
    enrollment = Enrolled.query.filter_by(
        student_id=current_user.id,
        schedule_id=schedule_id
    ).first_or_404()
    
    schedule = Schedule.query.get(schedule_id)
    schedule.current_enrollment -= 1
    
    try:
        db.session.delete(enrollment)
        db.session.commit()
        flash('Successfully dropped the course.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error dropping course: {str(e)}")
        flash('An error occurred while dropping the course.', 'error')
    
    return redirect(url_for('students.dashboard'))

@students.route('/academic-history')
@login_required
def academic_history():
    # Get all past enrollments with grades
    past_enrollments = (Enrolled.query
        .filter_by(student_id=current_user.id)
        .join(Schedule)
        .join(Course)
        .filter(Schedule.academic_year < datetime.now().year)
        .all())
    
    # Calculate GPA
    total_points = 0
    total_credits = 0
    for enrollment in past_enrollments:
        if enrollment.grade:
            grade_points = {
                'A': 4.0, 'A-': 3.7,
                'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                'C+': 2.3, 'C': 2.0, 'C-': 1.7,
                'D+': 1.3, 'D': 1.0, 'F': 0.0
            }.get(enrollment.grade, 0)
            total_points += grade_points * enrollment.schedule.course.credits
            total_credits += enrollment.schedule.course.credits
    
    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    return render_template('student/academic_history.html',
                         enrollments=past_enrollments,
                         gpa=gpa)

@students.route('/schedule')
@login_required
def view_schedule():
    # Get current semester enrollments
    current_year = datetime.now().year
    current_enrollments = (Enrolled.query
        .filter_by(student_id=current_user.id)
        .join(Schedule)
        .filter(Schedule.academic_year == current_year)
        .all())
    
    # Organize schedule by days
    schedule_by_day = {
        'Monday': [], 'Tuesday': [], 'Wednesday': [],
        'Thursday': [], 'Friday': []
    }
    
    for enrollment in current_enrollments:
        # Assuming schedule_time format includes day information
        # Example: "Monday 10:00 AM - 11:20 AM"
        day = enrollment.schedule.schedule_time.split()[0]
        if day in schedule_by_day:
            schedule_by_day[day].append(enrollment)
    
    return render_template('student/schedule.html',
                         schedule=schedule_by_day)

@students.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        # Pre-populate form with current user data
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        try:
            # Update basic information
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            
            # Handle password change if provided
            if form.current_password.data:
                if not check_password_hash(current_user.password, form.current_password.data):
                    flash('Current password is incorrect', 'error')
                    return render_template('student/profile.html', form=form)
                
                current_user.password = generate_password_hash(form.new_password.data)
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('students.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile', 'error')
            
    return render_template('student/profile.html', form=form) 