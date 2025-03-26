from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class StudentStatus(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    graduated = 'graduated'

class ProfessorStatus(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    retired = 'retired'

class CourseLevel(enum.Enum):
    undergraduate = 'undergraduate'
    graduate = 'graduate'
    doctoral = 'doctoral'

class Grade(enum.Enum):
    A = 'A'
    A_MINUS = 'A-'
    B_PLUS = 'B+'
    B = 'B'
    B_MINUS = 'B-'
    C_PLUS = 'C+'
    C = 'C'
    C_MINUS = 'C-'
    D_PLUS = 'D+'
    D = 'D'
    D_MINUS = 'D-'
    F = 'F'
    W = 'W'
    I = 'I'

class EnrollmentStatus(enum.Enum):
    enrolled = 'enrolled'
    dropped = 'dropped'
    completed = 'completed'
    withdrawn = 'withdrawn'

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    major = db.Column(db.String(50))
    enrollment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(StudentStatus), default=StudentStatus.active)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

class Professor(db.Model):
    __tablename__ = 'professor'
    professor_id = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(50))
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(ProfessorStatus), default=ProfessorStatus.active)
    teaching_assignments = db.relationship('Teaching', backref='professor', lazy=True)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.String(10), primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50))
    level = db.Column(db.Enum(CourseLevel), nullable=False)
    status = db.Column(db.String(10), default='active')
    prerequisites = db.relationship('Prerequisites', backref='course', lazy=True)
    schedules = db.relationship('Schedule', backref='course', lazy=True)

class Prerequisites(db.Model):
    __tablename__ = 'prerequisites'
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id', name='fk_prerequisites_course'), primary_key=True)
    prerequisite_id = db.Column(db.String(10), db.ForeignKey('course.course_id', name='fk_prerequisites_prereq'), primary_key=True)
    prerequisite = db.relationship('Course', foreign_keys=[prerequisite_id])

    __table_args__ = (
        db.CheckConstraint('course_id != prerequisite_id', name='chk_no_self_prerequisite'),
    )

class Schedule(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.String(10), primary_key=True)
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id', name='fk_schedule_course'))
    semester = db.Column(db.String(20), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)
    meeting_days = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room_number = db.Column(db.String(20))
    building = db.Column(db.String(50))
    max_capacity = db.Column(db.Integer, nullable=False, default=25)
    current_enrollment = db.Column(db.Integer, default=0)
    teaching_assignments = db.relationship('Teaching', backref='schedule', lazy=True)
    enrollments = db.relationship('Enrollment', backref='schedule', lazy=True)

    __table_args__ = (
        db.CheckConstraint("meeting_days REGEXP '^[MTWRF]+$'", name='chk_valid_meeting_days'),
    )

class Teaching(db.Model):
    __tablename__ = 'teaching'
    teaching_id = db.Column(db.String(10), primary_key=True)
    professor_id = db.Column(db.String(10), db.ForeignKey('professor.professor_id', name='fk_teaching_professor'))
    schedule_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id', name='fk_teaching_schedule'))

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.String(10), primary_key=True)
    student_id = db.Column(db.String(10), db.ForeignKey('student.student_id', name='fk_enrollment_student'))
    schedule_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id', name='fk_enrollment_schedule'))
    enrollment_date = db.Column(db.Date, nullable=False)
    grade = db.Column(db.Enum(Grade))
    status = db.Column(db.Enum(EnrollmentStatus), default=EnrollmentStatus.enrolled)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'schedule_id', name='uq_student_schedule'),
    ) 