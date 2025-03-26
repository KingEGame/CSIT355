from flask import render_template, redirect, url_for, session
from ..models import db, Professor, Schedule
from . import professors

@professors.route('/professors')
def list_professors():
    if 'student_id' not in session:
        return redirect(url_for('auth.index'))
    professors = Professor.query.all()
    return render_template('professors.html', professors=professors) 