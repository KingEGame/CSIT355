from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import or_
from datetime import datetime
from web.models import db, Student, StudentStatus, Schedule, Professor, Enrolled, Course, CourseLevel
from web.forms import StudentForm, ProfessorForm, CourseForm
from web.utils.decorators import admin_required
from sqlalchemy.exc import IntegrityError

admin = Blueprint('admin', __name__, url_prefix='/admin')

def current_year():
    return datetime.now().year

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_students': Student.query.count(),
        'active_courses': Schedule.query.filter_by(academic_year=current_year()).count(),
        'total_professors': Professor.query.count(),
        'active_enrollments': Enrolled.query.join(Schedule).filter(
            Schedule.academic_year == current_year()
        ).count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin.route('/students')
@login_required
@admin_required
def student_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Build the base query
    query = Student.query

    # Apply search filter
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            or_(
                Student.first_name.ilike(f'%{search}%'),
                Student.last_name.ilike(f'%{search}%'),
                Student.email.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%')
            )
        )

    # Apply status filter
    status = request.args.get('status')
    if status:
        query = query.filter(Student.status == StudentStatus(status))

    # Apply major filter (as substring)
    major = request.args.get('major')
    if major:
        query = query.filter(Student.major.ilike(f'%{major}%'))

    # Execute query with pagination
    pagination = query.order_by(Student.last_name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Build list of distinct majors for filter dropdown
    majors = [m[0] for m in db.session.query(Student.major).distinct().all()]

    return render_template(
        'admin/student_list.html',
        students=pagination.items,
        pagination=pagination,
        student_statuses=StudentStatus,
        majors=majors
    )

@admin.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            major=form.major.data,
            status=StudentStatus.active
        )
        # Set password if provided
        if form.password.data:
            student.set_password(form.password.data)

        try:
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('admin.student_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding student. Please try again.', 'error')

    return render_template('admin/student_form.html', form=form, title='Add Student')

@admin.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
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

        # Update password only if provided
        if form.password.data:
            student.set_password(form.password.data)

        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin.student_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student. Please try again.', 'error')

    return render_template(
        'admin/student_form.html',
        form=form,
        student=student,
        title='Edit Student'
    )

@admin.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    try:
        # Check if student has any enrollments
        if student.enrollments:
            flash('Cannot delete student with existing enrollments.', 'error')
            return redirect(url_for('admin.student_list'))

        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting student. Please try again.', 'error')

    return redirect(url_for('admin.student_list'))

@admin.route('/students/status')
@login_required
@admin_required
def student_status():
    # Get counts for each status
    status_counts = db.session.query(
        Student.status, db.func.count(Student.id)
    ).group_by(Student.status).all()

    # Format data for display
    status_data = {
        status.name: {
            'count': 0,
            'color': 'green' if status == StudentStatus.active
                    else 'red' if status == StudentStatus.inactive
                    else 'blue' if status == StudentStatus.graduated
                    else 'yellow'
        } for status in StudentStatus
    }
    
    for status, count in status_counts:
        status_data[status.name]['count'] = count

    return render_template('admin/student_status.html', status_data=status_data)

@admin.route('/professors')
@login_required
@admin_required
def professor_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Build the base query
    query = Professor.query

    # Apply search filter
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            or_(
                Professor.first_name.ilike(f'%{search}%'),
                Professor.last_name.ilike(f'%{search}%'),
                Professor.email.ilike(f'%{search}%'),
                Professor.department.ilike(f'%{search}%')
            )
        )

    # Apply department filter (as substring)
    department = request.args.get('department')
    if department:
        query = query.filter(Professor.department.ilike(f'%{department}%'))

    # Apply status filter
    status = request.args.get('status')
    if status:
        query = query.filter(Professor.status == status)

    # Execute query with pagination
    pagination = query.order_by(Professor.last_name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Build plain-department list
    departments = [d[0] for d in db.session.query(Professor.department).distinct().all()]

    return render_template(
        'admin/professor_list.html',
        professors=pagination.items,
        pagination=pagination,
        departments=departments
    )

@admin.route('/professors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_professor():
    form = ProfessorForm()
    if form.validate_on_submit():
        professor = Professor(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            department=form.department.data,
            office_location=form.office_location.data,
            office_hours=form.office_hours.data,
            phone=form.phone.data,
            status=form.status.data
        )
        # Set password if provided
        if form.password.data:
            professor.set_password(form.password.data)

        try:
            db.session.add(professor)
            db.session.commit()
            flash('Professor added successfully!', 'success')
            return redirect(url_for('admin.professor_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding professor. Please try again.', 'error')

    return render_template('admin/professor_form.html', form=form, title='Add Professor')

@admin.route('/professors/<int:professor_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    form = ProfessorForm(obj=professor)
    form.professor = professor  # Ensure correct email validation

    if form.validate_on_submit():
        professor.first_name = form.first_name.data
        professor.last_name = form.last_name.data
        professor.email = form.email.data
        professor.department = form.department.data
        professor.office_location = form.office_location.data
        professor.office_hours = form.office_hours.data
        professor.phone = form.phone.data
        professor.status = form.status.data

        # Update password only if provided
        if form.password.data:
            professor.set_password(form.password.data)

        try:
            db.session.commit()
            flash('Professor updated successfully!', 'success')
            return redirect(url_for('admin.professor_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating professor. Please try again.', 'error')

    return render_template(
        'admin/professor_form.html',
        form=form,
        professor=professor,
        title='Edit Professor'
    )

@admin.route('/professors/<int:professor_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    try:
        # Check if professor has any assigned courses
        if professor.schedules:
            flash('Cannot delete professor with assigned courses.', 'error')
            return redirect(url_for('admin.professor_list'))

        db.session.delete(professor)
        db.session.commit()
        flash('Professor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting professor. Please try again.', 'error')

    return redirect(url_for('admin.professor_list'))

@admin.route('/professors/teaching-load')
@login_required
@admin_required
def teaching_load():
    current_year = datetime.now().year
    professors = Professor.query.all()
    teaching_data = {}

    for professor in professors:
        current_courses = Schedule.query.filter_by(
            professor_id=professor.id,
            academic_year=current_year
        ).count()

        teaching_data[professor.id] = {
            'name': f"{professor.first_name} {professor.last_name}",
            'department': professor.department,
            'current_courses': current_courses,
            'status': professor.status
        }

    return render_template('admin/teaching_load.html', teaching_data=teaching_data)

@admin.route('/courses')
@admin_required
def course_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build query with filters
    query = Course.query
    
    # Apply search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            or_(
                Course.code.ilike(f'%{search}%'),
                Course.name.ilike(f'%{search}%')
            )
        )
    
    # Apply department filter (as substring)
    department = request.args.get('department')
    if department:
        query = query.filter(Course.department.ilike(f'%{department}%'))
    
    # Apply level filter
    level = request.args.get('level')
    if level:
        query = query.filter(Course.level == CourseLevel[level])
    
    # Get paginated results
    pagination = query.order_by(Course.code).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Build plain department list
    departments = [d[0] for d in db.session.query(Course.department).distinct().all()]

    return render_template(
        'admin/course_list.html',
        courses=pagination.items,
        pagination=pagination,
        departments=departments,
        course_levels=CourseLevel
    )

@admin.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    form = CourseForm()
    
    if form.validate_on_submit():
        try:
            # Create new course
            course = Course(
                code=form.code.data.upper(),
                name=form.name.data,
                description=form.description.data,
                department=form.department.data,
                level=CourseLevel[form.level.data],
                credits=form.credits.data,
                is_active=form.is_active.data
            )
            
            # Handle prerequisites
            if form.prerequisites.data:
                prereq_codes = [code.strip() for code in form.prerequisites.data.split(',')]
                prereqs = Course.query.filter(Course.code.in_(prereq_codes)).all()
                course.prerequisites.extend(prereqs)
            
            db.session.add(course)
            db.session.commit()
            
            flash('Course added successfully.', 'success')
            return redirect(url_for('admin.course_list'))
            
        except IntegrityError:
            db.session.rollback()
            flash('A course with this code already exists.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
    
    return render_template('admin/course_form.html', form=form, title='Add Course')

@admin.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        try:
            # Update basic course info
            form.populate_obj(course)
            course.code = course.code.upper()
            course.department = form.department.data
            course.level = CourseLevel[form.level.data]
            
            # Update prerequisites
            course.prerequisites.clear()
            if form.prerequisites.data:
                prereq_codes = [code.strip() for code in form.prerequisites.data.split(',')]
                prereqs = Course.query.filter(Course.code.in_(prereq_codes)).all()
                course.prerequisites.extend(prereqs)
            
            db.session.commit()
            flash('Course updated successfully.', 'success')
            return redirect(url_for('admin.course_list'))
            
        except IntegrityError:
            db.session.rollback()
            flash('A course with this code already exists.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
    
    # Pre-populate prerequisites field
    if course.prerequisites and not form.prerequisites.data:
        form.prerequisites.data = ', '.join([p.code for p in course.prerequisites])
    
    return render_template(
        'admin/course_form.html',
        form=form,
        course=course,
        title='Edit Course'
    )

@admin.route('/courses/<int:course_id>/delete', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    try:
        # Check if course has any active schedules
        if course.schedules.filter_by(is_active=True).first():
            flash('Cannot delete course with active schedules.', 'error')
            return redirect(url_for('admin.course_list'))
        
        # Check if course is a prerequisite for other courses
        if course.dependent_courses.first():
            flash('Cannot delete course that is a prerequisite for other courses.', 'error')
            return redirect(url_for('admin.course_list'))
        
        # Delete the course
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('admin.course_list')) 