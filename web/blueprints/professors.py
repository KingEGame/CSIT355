from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from web.models import db, Schedule, User, CourseMaterial
from web.utils import professor_required

professors = Blueprint('professors', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@professors.route('/course-management')
@login_required
@professor_required
def course_management():
    # Get all courses taught by the professor for the current semester
    current_year = datetime.now().year
    courses = Schedule.query.join(User, Schedule.professor_id == User.id)\
        .filter(Schedule.professor_id == current_user.id)\
        .filter(Schedule.year == current_year)\
        .all()

    # For each course, get enrolled students
    for course in courses:
        course.students = User.query.join(Enrolled, User.id == Enrolled.student_id)\
            .filter(Enrolled.schedule_id == course.schedule_id)\
            .all()

    return render_template('professor/course_management.html', courses=courses)

@professors.route('/upload-material', methods=['POST'])
@login_required
@professor_required
def upload_material():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('professors.course_management'))
    
    file = request.files['file']
    course_id = request.form.get('course_id')
    title = request.form.get('title')

    if not file or not course_id or not title:
        flash('Missing required information', 'error')
        return redirect(url_for('professors.course_management'))

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('professors.course_management'))

    if not allowed_file(file.filename):
        flash('Invalid file type', 'error')
        return redirect(url_for('professors.course_management'))

    # Verify the course belongs to the professor
    course = Schedule.query.filter_by(
        schedule_id=course_id,
        professor_id=current_user.id
    ).first()

    if not course:
        flash('Course not found or access denied', 'error')
        return redirect(url_for('professors.course_management'))

    try:
        filename = secure_filename(file.filename)
        # Create unique filename to avoid collisions
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(course_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # Create database record
        material = CourseMaterial(
            course_id=course_id,
            title=title,
            file_path=file_path
        )
        db.session.add(material)
        db.session.commit()

        flash('Material uploaded successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to upload material', 'error')
        current_app.logger.error(f"Error uploading material: {str(e)}")

    return redirect(url_for('professors.course_management'))

@professors.route('/materials/<int:material_id>', methods=['DELETE'])
@login_required
@professor_required
def delete_material(material_id):
    material = CourseMaterial.query.join(Schedule)\
        .filter(CourseMaterial.id == material_id)\
        .filter(Schedule.professor_id == current_user.id)\
        .first()

    if not material:
        return 'Material not found or access denied', 404

    try:
        # Delete file from filesystem
        if os.path.exists(material.file_path):
            os.remove(material.file_path)

        # Delete database record
        db.session.delete(material)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting material: {str(e)}")
        return 'Failed to delete material', 500

@professors.route('/materials/<int:material_id>/download')
@login_required
@professor_required
def download_material(material_id):
    material = CourseMaterial.query.join(Schedule)\
        .filter(CourseMaterial.id == material_id)\
        .filter(Schedule.professor_id == current_user.id)\
        .first()

    if not material or not os.path.exists(material.file_path):
        flash('Material not found', 'error')
        return redirect(url_for('professors.course_management'))

    return send_file(
        material.file_path,
        as_attachment=True,
        download_name=os.path.basename(material.file_path)
    ) 