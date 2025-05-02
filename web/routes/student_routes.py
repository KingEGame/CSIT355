from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Student, StudentStatus, Schedule, Enrolled, EnrollmentStatus, Course, CourseLevel, Semester
from datetime import datetime
from flask_login import login_required, current_user
from ..forms import StudentForm

students = Blueprint('students', __name__)

@students.route('/student/profile', methods=['GET', 'POST'])
def profile():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))

    form = StudentForm(obj=student)

    if request.method == 'POST':
        if form.validate_on_submit():
            student.first_name = form.first_name.data
            student.last_name = form.last_name.data
            student.email = form.email.data
            student.major = form.major.data
            try:
                db.session.commit()
                flash('Profile updated successfully.', 'success')
                return redirect(url_for('students.profile'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating profile: {str(e)}', 'error')
        else:
            flash('Please correct the errors in the form.', 'error')

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

    total_credits = sum(
        current_enrollments[i].schedule.course.credits
        for i in range(len(current_enrollments))
        if current_enrollments[i].status == EnrollmentStatus.enrolled
    )

    # Initialize a dummy form for CSRF protection
    form = StudentForm()
    courses_to_completion = total_credits/120

    return render_template('student/dashboard.html', 
                           student=student, 
                           enrollments=current_enrollments, 
                           completed_credits=completed_credits,
                           total_credits=total_credits,
                           form=form,
                           courses_to_completion=courses_to_completion
                        )

@students.route('/student/academic-history')
def academic_history():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))
    
    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))
    
    enrollments = student.enrollments
    completed_courses = [e for e in student.enrollments if e.status == EnrollmentStatus.completed or e.grade is not None]
    gpa = student.get_gpa()
    attempted_credits = sum(e.schedule.course.credits for e in enrollments if e.status != EnrollmentStatus.dropped)
    completed_credits = sum(e.schedule.course.credits for e in enrollments if e.status == EnrollmentStatus.completed)
    return render_template(
        'student/academic_history.html',
        student=student,
        enrollments=enrollments,
        completed_courses=completed_courses,
        gpa=gpa,
        attempted_credits=attempted_credits,
        completed_credits=completed_credits
    )

@students.route('/student/academic-history/download-csv')
def download_academic_history_csv():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))
    import csv
    from io import StringIO
    student = Student.query.get(session['student_id'])
    enrollments = student.enrollments
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Year/Semester', 'Course Code', 'Course Name', 'Professor', 'Credits', 'Level', 'Status', 'Grade'])
    for e in enrollments:
        prof = e.schedule.professors[0].last_name if e.schedule.professors and len(e.schedule.professors) > 0 else ''
        writer.writerow([
            f"{e.schedule.academic_year} {e.schedule.semester}",
            e.schedule.course.course_code,
            e.schedule.course.course_name,
            prof,
            e.schedule.course.credits,
            e.schedule.course.level.value.capitalize(),
            e.status.value.capitalize(),
            e.grade if e.grade else 'N/A'
        ])
    output.seek(0)
    from flask import Response
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=academic_history.csv"})

@students.route('/student/available-courses')
def available_courses():
    if 'student_id' not in session:
        return redirect(url_for('auth.login'))

    student = Student.query.get(session['student_id'])
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('auth.login'))

    # Get filter and sort parameters from request
    search = request.args.get('search', '').strip()
    semester = request.args.get('semester', '').strip()
    level = request.args.get('level', '').strip()
    sort = request.args.get('sort', 'course_code')  # default sort
    sort_dir = request.args.get('sort_dir', 'asc')

    allowed_levels = get_allowed_course_levels(student.level)

    # Build the base query
    query = Schedule.query.join(Course).filter(
        Course.level.in_(allowed_levels)
    )

    # Apply search filter
    if search:
        query = query.filter(
            (Course.course_code.ilike(f"%{search}%")) |
            (Course.course_name.ilike(f"%{search}%"))
        )

    # Apply semester filter
    if semester:
        query = query.filter(Schedule.semester == semester)

    # Apply level filter
    if level:
        query = query.filter(Course.level == level)

    # Sorting
    sort_options = {
        'course_code': Course.course_code,
        'course_name': Course.course_name,
        'credits': Course.credits,
        'semester': Schedule.semester,
        'academic_year': Schedule.academic_year
    }
    sort_column = sort_options.get(sort, Course.course_code)
    if sort_dir == 'desc':
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()
    query = query.order_by(sort_column)

    schedules = query.all()

    # Dynamically filter schedules with available spots and annotate with enrolled count
    available_schedules = []
    for schedule in schedules:
        enrolled_count = sum(1 for e in schedule.enrollments if e.status == EnrollmentStatus.enrolled)
        if enrolled_count < schedule.course.max_capacity:
            schedule._enrolled_count = enrolled_count  # attach for template use
            available_schedules.append(schedule)

    # Get student's current enrollments to check for duplicates
    student_enrollments = Enrolled.query.filter_by(
        student_id=session['student_id']
    ).all()
    enrolled_schedule_ids = [e.schedule_id for e in student_enrollments]

    # For filter dropdowns
    semesters = list(Semester)
    course_levels = list(CourseLevel)

    # Initialize a dummy form for CSRF protection
    form = StudentForm()

    return render_template('student/available_courses.html',
                         schedules=available_schedules,
                         enrolled_schedule_ids=enrolled_schedule_ids,
                         student_level=student.level,
                         semesters=semesters,
                         course_levels=course_levels,
                         form=form,
                         search=search,
                         semester=semester,
                         level=level,
                         sort=sort,
                         sort_dir=sort_dir)

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

@students.route('/student/register_course', methods=['POST'])
def register_course():
    if 'student_id' not in session:
        flash('You must be logged in to register for a course.', 'error')
        return redirect(url_for('auth.login'))

    schedule_id = request.form.get('schedule_id')
    print(f"Debug: schedule_id={schedule_id}, student_id={session.get('student_id')}")

    try:
        student = Student.query.get(session['student_id'])
        if not student:
            flash('Student not found.', 'error')
            return redirect(url_for('students.available_courses'))

        # Check if already enrolled - using the shared session
        existing_enrollment = Enrolled.query.filter_by(
            student_id=session['student_id'],
            schedule_id=schedule_id
        ).first()

        if existing_enrollment:
            if existing_enrollment.status == EnrollmentStatus.dropped:
                existing_enrollment.status = EnrollmentStatus.enrolled
                db.session.commit()
                flash('Successfully re-registered for the course.', 'success')
                return redirect(url_for('students.dashboard'))
            flash('You are already enrolled in this course.', 'error')
            return redirect(url_for('students.available_courses'))

        # Get course and schedule information - using the shared session
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            flash('Course schedule not found.', 'error')
            return redirect(url_for('students.available_courses'))

        # Prerequisite check
        course = schedule.course
        prerequisites = course.prerequisites.all() if hasattr(course.prerequisites, 'all') else course.prerequisites
        missing_prereqs = []
        for prereq in prerequisites:
            completed = any(
                e.schedule.course.course_id == prereq.course_id and e.status == EnrollmentStatus.completed
                for e in student.enrollments
            )
            if not completed:
                missing_prereqs.append(prereq.course_code)
        if missing_prereqs:
            flash(f"Cannot register: Missing prerequisite(s): {', '.join(missing_prereqs)}.", 'error')
            return redirect(url_for('students.available_courses'))

        # Schedule conflict check
        new_days = set(schedule.meeting_days)
        new_start = schedule.start_time
        new_end = schedule.end_time
        current_enrollments = Enrolled.query.filter_by(
            student_id=session['student_id'],
            status=EnrollmentStatus.enrolled
        ).all()
        for enrollment in current_enrollments:
            other_schedule = enrollment.schedule
            overlap_days = new_days.intersection(set(other_schedule.meeting_days))
            if overlap_days:
                if (new_start < other_schedule.end_time and new_end > other_schedule.start_time):
                    flash(
                        f"Schedule conflict with {other_schedule.course.course_code} on {', '.join(overlap_days)} "
                        f"({other_schedule.start_time.strftime('%H:%M')}-{other_schedule.end_time.strftime('%H:%M')})",
                        'error'
                    )
                    return redirect(url_for('students.available_courses'))

        # Check if the course has reached maximum enrollment
        enrolled_count = sum(1 for e in schedule.enrollments if e.status == EnrollmentStatus.enrolled)
        if enrolled_count >= schedule.course.max_capacity:
            flash('Cannot register: The course has reached its maximum enrollment.', 'error')
            return redirect(url_for('students.available_courses'))

        # Create new enrollment within the same transaction
        enrollment = Enrolled(
            student_id=session['student_id'],
            schedule_id=schedule_id,
            status=EnrollmentStatus.enrolled
        )

        db.session.add(enrollment)
        db.session.commit()
        print(f"Debug: Enrollment created for schedule_id={schedule_id}")

        flash('Course registered successfully.', 'success')
        return redirect(url_for('students.dashboard'))

    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        print(f"Error: {error_message}")
        if 'Cannot enroll: Course has reached maximum enrollment' in error_message:
            flash('Cannot register: The course has reached its maximum enrollment.', 'error')
        else:
            flash(f'Error registering for the course: {error_message}', 'error')
        return redirect(url_for('students.available_courses'))

@students.route('/student/drop_course', methods=['POST'])
def drop_course():
    print(f"Debug: Request form data: {request.form}")

    if 'student_id' not in session:
        flash('You must be logged in to drop a course.', 'error')
        return redirect(url_for('auth.login'))

    enrollment_id = request.form.get('enrollment_id')
    print(f"Debug: enrollment_id={enrollment_id}, student_id={session.get('student_id')}")

    try:
        enrollment = Enrolled.query.filter_by(
            enrollment_id=enrollment_id,
            student_id=session['student_id']
        ).first()

        if not enrollment:
            flash('Enrollment not found.', 'error')
            return redirect(url_for('students.dashboard'))

        if enrollment.status != EnrollmentStatus.enrolled:
            flash('Cannot drop this course at this time.', 'error')
            return redirect(url_for('students.dashboard'))

        enrollment.status = EnrollmentStatus.dropped
        db.session.commit()
        print(f"Debug: Enrollment {enrollment_id} status updated to dropped.")

        flash('Course successfully dropped.', 'success')
        return redirect(url_for('students.dashboard'))

    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        print(f"Error: {error_message}")
        flash(f'Error dropping the course: {error_message}', 'error')
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

    # Initialize a dummy form for CSRF protection
    form = StudentForm()

    return render_template('student/schedule.html', enrollments=current_enrollments, form=form)