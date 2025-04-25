from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class StudentStatus(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    graduated = 'graduated'
    suspended = 'suspended'
    on_leave = 'on_leave'

class ProfessorStatus(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    retired = 'retired'

class CourseLevel(enum.Enum):
    undergraduate = 'undergraduate'
    graduate = 'graduate'
    phd = 'phd'

class Semester(enum.Enum):
    Fall = 'Fall'
    Spring = 'Spring'
    Summer = 'Summer'

class Grade(enum.Enum):
    A_PLUS = 'A+'
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
    F = 'F'
    W = 'W'
    I = 'I'

class EnrollmentStatus(enum.Enum):
    enrolled = 'enrolled'
    dropped = 'dropped'
    withdrawn = 'withdrawn'
    completed = 'completed'

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    major = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(StudentStatus), default=StudentStatus.active)
    level = db.Column(db.Enum(CourseLevel), default=CourseLevel.undergraduate)
    enrollment_date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    total_credits = db.Column(db.Integer, default=0)
    enrollments = db.relationship('Enrolled', backref='student', lazy=True)

    __table_args__ = (
        db.CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='student_email_format_check'),
        db.Index('idx_student_email', 'email'),
        db.Index('idx_student_status', 'status')
    )

    @staticmethod
    def validate_age(date_of_birth):
        """Validate that the student is at least 16 years old"""
        from datetime import datetime, timedelta
        min_birth_date = datetime.now().date() - timedelta(days=16*365)
        return date_of_birth <= min_birth_date

class Professor(db.Model):
    __tablename__ = 'professor'
    professor_id = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    office_number = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    teaching_assignments = db.relationship('Teaching', backref='professor', lazy=True)

    __table_args__ = (
        db.CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_professor_email'),
        db.Index('idx_professor_email', 'email'),
        db.Index('idx_professor_department', 'department')
    )

class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.String(10), primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Enum(CourseLevel), default=CourseLevel.undergraduate)
    max_capacity = db.Column(db.Integer, default=30)
    schedules = db.relationship('Schedule', backref='course', lazy=True)
    
    # Define prerequisites relationship
    prerequisites = db.relationship(
        'Course',
        secondary='prerequisite',
        primaryjoin=('Course.course_id == prerequisite.c.course_id'),
        secondaryjoin=('Course.course_id == prerequisite.c.prerequisite_course_id'),
        backref=db.backref('required_for', lazy='dynamic'),
        lazy='dynamic',
        viewonly=True
    )

    __table_args__ = (
        db.CheckConstraint('credits BETWEEN 1 AND 6', name='chk_course_credits'),
        db.CheckConstraint('max_capacity BETWEEN 5 AND 300', name='chk_course_capacity'),
        db.Index('idx_course_code', 'course_code'),
        db.Index('idx_course_department', 'department')
    )

class Prerequisite(db.Model):
    __tablename__ = 'prerequisite'
    prerequisite_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(10), db.ForeignKey('courses.course_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    prerequisite_course_id = db.Column(db.String(10), db.ForeignKey('courses.course_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'prerequisite_course_id', name='unique_prerequisite'),
    )

    @staticmethod
    def validate_no_self_prerequisite(course_id, prerequisite_course_id):
        """Validate that a course cannot be its own prerequisite"""
        return course_id != prerequisite_course_id

    def __init__(self, **kwargs):
        if not self.validate_no_self_prerequisite(kwargs.get('course_id'), kwargs.get('prerequisite_course_id')):
            raise ValueError("A course cannot be its own prerequisite")
        super().__init__(**kwargs)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.String(10), primary_key=True)
    course_id = db.Column(db.String(10), db.ForeignKey('courses.course_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    semester = db.Column(db.Enum(Semester), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    meeting_days = db.Column(db.String(10), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    current_enrollment = db.Column(db.Integer, default=0)
    teaching_assignments = db.relationship('Teaching', backref='schedule', lazy=True)
    enrollments = db.relationship('Enrolled', backref='schedule', lazy=True)

    __table_args__ = (
        db.CheckConstraint("meeting_days REGEXP '^[MTWRF]+$'", name='chk_schedule_days'),
        db.CheckConstraint('start_time < end_time', name='chk_schedule_time'),
        db.Index('idx_schedule_semester', 'semester')
    )

    def validate_enrollment_capacity(self):
        """Validate that current enrollment doesn't exceed course max capacity"""
        if self.current_enrollment > self.course.max_capacity:
            raise ValueError(f"Current enrollment ({self.current_enrollment}) cannot exceed course maximum capacity ({self.course.max_capacity})")
        return True

class Enrolled(db.Model):
    __tablename__ = 'enrolled'
    enrollment_id = db.Column(db.String(10), primary_key=True)
    student_id = db.Column(db.String(10), db.ForeignKey('student.student_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    schedule_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    grade = db.Column(db.Enum(Grade))
    status = db.Column(db.Enum(EnrollmentStatus), default=EnrollmentStatus.enrolled)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'schedule_id', name='unique_enrollment'),
        db.Index('idx_enrollment_status', 'status')
    )

class Teaching(db.Model):
    __tablename__ = 'teaching'
    teaching_id = db.Column(db.String(10), primary_key=True)
    professor_id = db.Column(db.String(10), db.ForeignKey('professor.professor_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    schedule_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('professor_id', 'schedule_id', name='unique_teaching_assignment'),
    )

class CourseMaterial(db.Model):
    __tablename__ = 'course_materials'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    course = db.relationship('Schedule', backref=db.backref('materials', lazy=True))

    def __repr__(self):
        return f'<CourseMaterial {self.title}>'

# Modify the event listener to include capacity validation
@db.event.listens_for(Enrolled, 'before_insert')
def validate_enrollment_before_insert(mapper, connection, target):
    schedule = db.session.get(Schedule, target.schedule_id)
    if schedule.current_enrollment >= schedule.course.max_capacity:
        raise ValueError(f"Cannot enroll: Course has reached maximum capacity of {schedule.course.max_capacity}")

@db.event.listens_for(Enrolled, 'after_insert')
def update_enrollment_count_after_insert(mapper, connection, target):
    connection.execute(
        Schedule.__table__.update().
        where(Schedule.schedule_id == target.schedule_id).
        values(current_enrollment=Schedule.current_enrollment + 1)
    )

@db.event.listens_for(Enrolled, 'after_delete')
def update_enrollment_count_after_delete(mapper, connection, target):
    connection.execute(
        Schedule.__table__.update().
        where(Schedule.schedule_id == target.schedule_id).
        values(current_enrollment=Schedule.current_enrollment - 1)
    ) 