from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, Course, Professor, Schedule, Teaching, CourseLevel, Semester, StudentStatus
from datetime import datetime
from web.models import Student
from web.forms import StudentForm, ProfessorForm, CourseForm
from flask_wtf.csrf import generate_csrf

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
    total_students = db.session.query(db.func.count()).select_from(db.Model.metadata.tables['student']).scalar()
    total_professors = db.session.query(db.func.count()).select_from(db.Model.metadata.tables['professor']).scalar()
    total_courses = db.session.query(db.func.count()).select_from(db.Model.metadata.tables['courses']).scalar()
    total_enrollments = db.session.query(db.func.count()).select_from(db.Model.metadata.tables['enrolled']).scalar()
    stats = {
        'total_students': total_students,
        'active_courses': total_courses,  # No active field, so use total
        'total_professors': total_professors,
        'active_enrollments': total_enrollments  # No active field, so use total
    }
    courses = Course.query.all()
    professors = Professor.query.all()
    schedules = Schedule.query.all()
    return render_template('admin/dashboard.html',
                         courses=courses,
                         professors=professors,
                         schedules=schedules,
                         stats=stats)

@admin.route('/admin/courses')
def course_list():
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()
    level = request.args.get('level', '').strip()

    query = Course.query
    if search:
        query = query.filter(
            (Course.course_code.ilike(f'%{search}%')) |
            (Course.course_name.ilike(f'%{search}%'))
        )
    if department:
        query = query.filter(Course.department == department)
    if level:
        query = query.filter(Course.level == level)

    courses = query.all()

    # For dropdowns
    departments = db.session.query(Course.department).distinct().all()
    departments = [{'name': row[0], 'value': row[0]} for row in departments if row[0]]
    course_levels = [{'name': lvl.name, 'value': lvl.value.capitalize()} for lvl in CourseLevel]

    return render_template(
        'admin/course_list.html',
        courses=courses,
        departments=departments,
        course_levels=course_levels
    )

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

@admin.route('/admin/students')
def student_list():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    major = request.args.get('major', '').strip()

    query = Student.query
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) |
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.email.ilike(f'%{search}%')) |
            (Student.student_id.ilike(f'%{search}%'))
        )
    if status:
        query = query.filter(Student.status == status)
    if major:
        query = query.filter(Student.major == major)

    # Pagination (optional, adjust as needed)
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Student.student_id).paginate(page=page, per_page=20, error_out=False)
    students = pagination.items

    # Calculate completed_credits for each student
    for student in students:
        completed_credits = 0
        for e in getattr(student, 'enrollments', []):
            if hasattr(e, 'status') and hasattr(e, 'schedule') and hasattr(e.schedule, 'course'):
                if (getattr(e, 'status', None) and getattr(e, 'status', None).name == 'completed') or getattr(e, 'grade', None) is not None:
                    completed_credits += getattr(e.schedule.course, 'credits', 0)
        student.completed_credits = completed_credits

    # Get all unique statuses and majors for the filter dropdowns
    student_statuses = StudentStatus
    majors = [row[0] for row in db.session.query(Student.major).distinct().all()]

    return render_template('admin/student_list.html',
                           students=students,
                           student_statuses=student_statuses,
                           majors=majors,
                           pagination=pagination,
                           csrf_token=generate_csrf())

@admin.route('/admin/students/add', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            student_id=request.form.get('student_id') or None,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            major=form.major.data,
            status=form.status.data,
            date_of_birth=datetime.now().date(),  # Placeholder, should be in form
            level=None  # Set as needed
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('admin.student_list'))
    return render_template('admin/student_form.html', form=form)

@admin.route('/admin/professors')
def professor_list():
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()

    query = Professor.query
    if search:
        query = query.filter(
            (Professor.first_name.ilike(f'%{search}%')) |
            (Professor.last_name.ilike(f'%{search}%')) |
            (Professor.email.ilike(f'%{search}%')) |
            (Professor.department.ilike(f'%{search}%'))
        )
    if department:
        query = query.filter(Professor.department == department)

    # Pagination (optional, adjust as needed)
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Professor.professor_id).paginate(page=page, per_page=20, error_out=False)
    professors = pagination.items

    # Get all unique departments for the filter dropdown
    departments = db.session.query(Professor.department).distinct().all()
    departments = [{'name': row[0], 'value': row[0]} for row in departments if row[0]]

    return render_template('admin/professor_list.html',
                           professors=professors,
                           departments=departments,
                           pagination=pagination,
                           csrf_token=generate_csrf())

@admin.route('/admin/professors/add', methods=['GET', 'POST'])
def add_professor():
    form = ProfessorForm()
    return render_template('admin/professor_form.html', form=form)

@admin.route('/admin/professors/<professor_id>/edit', methods=['GET', 'POST'])
def edit_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    form = ProfessorForm(obj=professor)
    form.professor = professor  # Ensure correct email validation
    if form.validate_on_submit():
        form.populate_obj(professor)
        db.session.commit()
        flash('Professor updated successfully!', 'success')
        return redirect(url_for('admin.professor_list'))
    return render_template('admin/professor_form.html', form=form, professor=professor)

@admin.route('/admin/professors/<professor_id>/delete', methods=['POST'])
def delete_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    try:
        # Delete all teaching assignments for this professor
        for teaching in list(professor.teaching_assignments):
            db.session.delete(teaching)
        db.session.delete(professor)
        db.session.commit()
        flash('Professor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting professor: {str(e)}', 'error')
    return redirect(url_for('admin.professor_list'))

@admin.route('/admin/courses/add', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()
    return render_template('admin/course_form.html', form=form)

@admin.route('/admin/courses/<course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    return render_template('admin/course_form.html', form=form, course=course)

@admin.route('/admin/courses/<course_id>/delete', methods=['POST'])
def delete_course(course_id):
    flash(f'Delete course {course_id} (not implemented)', 'warning')
    return redirect(url_for('admin.course_list'))

@admin.route('/admin/teaching-assignments')
def teaching_assignments():
    department_filter = request.args.get('department', '').strip()
    status_filter = request.args.get('status', '').strip()
    teaching_data = {}
    professors = Professor.query.all()
    for prof in professors:
        # Get all teaching assignments for this professor
        teaching_assignments = prof.teaching_assignments if hasattr(prof, 'teaching_assignments') else []
        courses = []
        for t in teaching_assignments:
            if hasattr(t, 'schedule') and hasattr(t.schedule, 'course'):
                courses.append({'code': t.schedule.course.course_code})
        current_courses = len(courses)
        status_value = prof.status.value if hasattr(prof.status, 'value') else str(prof.status)
        # Apply filters
        if (not department_filter or prof.department == department_filter) and (not status_filter or status_value == status_filter):
            teaching_data[prof.professor_id] = {
                'name': f"{prof.first_name} {prof.last_name}",
                'email': prof.email,
                'office_number': getattr(prof, 'office_number', None),
                'department': prof.department,
                'current_courses': current_courses,
                'courses': courses,
                'status': status_value,
            }
    return render_template('admin/teaching_load.html', teaching_data=teaching_data)

@admin.route('/admin/students/<student_id>/delete', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    try:
        # Delete all enrollments for this student
        for enrollment in list(student.enrollments):
            db.session.delete(enrollment)
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
    return redirect(url_for('admin.student_list'))

@admin.route('/admin/students/<student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    form.student = student  # Ensure correct email validation
    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.email = form.email.data
        student.major = form.major.data
        student.status = form.status.data
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin.student_list'))
    return render_template('admin/student_form.html', form=form, student=student)

@admin.route('/admin/schedules')
def schedule_list():
    schedules = Schedule.query.all()
    courses = {c.course_id: c for c in Course.query.all()}
    professors = {p.professor_id: p for p in Professor.query.all()}
    return render_template('admin/schedule_list.html', schedules=schedules, courses=courses, professors=professors) 