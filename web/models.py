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
    enrollments = db.relationship('Enrolled', backref='student', lazy=True)
    __table_args__ = (
        db.CheckConstraint("email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='student_email_format_check'),
        db.CheckConstraint("date_of_birth <= CURRENT_DATE - INTERVAL 16 YEAR", name='chk_student_dob'),
        db.Index('idx_student_email', 'email'),
        db.Index('idx_student_status', 'status')
    )

    @staticmethod
    def validate_age(date_of_birth):
        """Validate that the student is at least 16 years old"""
        from datetime import datetime, timedelta
        min_birth_date = datetime.now().date() - timedelta(days=16*365)
        return date_of_birth <= min_birth_date

    def can_upgrade_level(self):
        """Check if student can upgrade their academic level"""
        if self.level == CourseLevel.undergraduate:
            # Check if student has completed required credits for graduation
            completed_credits = sum(
                enrollment.schedule.course.credits 
                for enrollment in self.enrollments 
                if enrollment.status == EnrollmentStatus.completed
            )
            return completed_credits >= 120  # Typical undergraduate requirement
        elif self.level == CourseLevel.graduate:
            # Check if student has completed required graduate credits
            completed_credits = sum(
                enrollment.schedule.course.credits 
                for enrollment in self.enrollments 
                if enrollment.status == EnrollmentStatus.completed 
                and enrollment.schedule.course.level == CourseLevel.graduate
            )
            return completed_credits >= 30  # Typical master's requirement
        return False

    def get_gpa(self):
        """Calculate student's GPA"""
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'F': 0.0
        }
        
        completed_courses = [e for e in self.enrollments if e.grade in grade_points]
        if not completed_courses:
            return 0.0
        
        total_points = sum(grade_points[e.grade] * e.schedule.course.credits for e in completed_courses)
        total_credits = sum(e.schedule.course.credits for e in completed_courses)
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    def get_completed_credits(self):
        """Get total completed credits"""
        return sum(
            enrollment.schedule.course.credits 
            for enrollment in self.enrollments 
            if enrollment.status == EnrollmentStatus.completed
        )

    def get_current_enrolled_credits(self):
        """Get total credits for currently enrolled courses"""
        return sum(
            enrollment.schedule.course.credits
            for enrollment in self.enrollments
            if enrollment.status == EnrollmentStatus.enrolled
        )

    def get_total_credits(self):
        """Calculate total credits including completed and currently enrolled courses"""
        completed_credits = sum(
            enrollment.schedule.course.credits
            for enrollment in self.enrollments
            if enrollment.status == EnrollmentStatus.completed
        )
        current_enrolled_credits = sum(
            enrollment.schedule.course.credits
            for enrollment in self.enrollments
            if enrollment.status == EnrollmentStatus.enrolled
        )
        return completed_credits + current_enrolled_credits

    @property
    def is_active(self):
        """Return True if the student is active."""
        return self.status == StudentStatus.active

    # Flask-Login required properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        """Return the student's ID."""
        return self.student_id

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

    @property
    def status(self):
        from .models import ProfessorStatus  # avoid circular import if any
        return ProfessorStatus.active

    @property
    def is_active(self):
        """Return True if the professor is active."""
        return self.status == ProfessorStatus.active

    @property
    def office_hours(self):
        """Return a dictionary of office hours dynamically fetched from the database."""
        return {
            "Monday": self.office_hours_monday,
            "Tuesday": self.office_hours_tuesday,
            "Wednesday": self.office_hours_wednesday,
            "Thursday": self.office_hours_thursday,
            "Friday": self.office_hours_friday
        }

    # Flask-Login required properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        """Return the professor's ID."""
        return self.professor_id

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
        db.CheckConstraint('course_id != prerequisite_course_id', name='no_self_prerequisite'),
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
    academic_year = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    meeting_days = db.Column(db.String(10), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    max_enrollment = db.Column(db.Integer, nullable=False)
    teaching_assignments = db.relationship('Teaching', backref='schedule', lazy=True)
    enrollments = db.relationship('Enrolled', backref='schedule', lazy=True)
    professors = db.relationship(
        'Professor',
        secondary='teaching',
        backref=db.backref('teaching_schedules', lazy='dynamic')
    )
    __table_args__ = (
        db.Index('idx_schedule_semester', 'semester', 'academic_year'),
        db.CheckConstraint('start_time < end_time', name='chk_schedule_time'),
        db.CheckConstraint("meeting_days REGEXP '^[MTWRF]+$'", name='chk_schedule_days'),
        # db.CheckConstraint('academic_year >= YEAR(CURRENT_DATE)', name='chk_academic_year'),  # Removed for MySQL compatibility
    )

class Enrolled(db.Model):
    __tablename__ = 'enrolled'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(10), db.ForeignKey('student.student_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    schedule_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    grade = db.Column(db.String(2))
    status = db.Column(db.Enum(EnrollmentStatus), default=EnrollmentStatus.enrolled)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'schedule_id', name='unique_enrollment'),
        db.Index('idx_enrollment_status', 'status'),
        db.CheckConstraint("grade IN ('A+','A','A-','B+','B','B-','C+','C','C-','D+','D','F','W','I')", name='chk_grade')
    )

class Teaching(db.Model):
    __tablename__ = 'teaching'
    teaching_id = db.Column(db.String(10), primary_key=True)
    professor_id = db.Column(db.String(10), db.ForeignKey('professor.professor_id'))
    schedule_id = db.Column(db.String(10), db.ForeignKey('schedule.schedule_id'))

    __table_args__ = (
        db.UniqueConstraint('professor_id', 'schedule_id', name='unique_teaching_assignment'),
    )

# Add ORM-level triggers to prevent self-prerequisites
@db.event.listens_for(Prerequisite, 'before_insert')
def validate_prerequisite_no_self_insert(mapper, connection, target):
    if target.course_id == target.prerequisite_course_id:
        raise ValueError('A course cannot be a prerequisite of itself')

@db.event.listens_for(Prerequisite, 'before_update')
def validate_prerequisite_no_self_update(mapper, connection, target):
    if target.course_id == target.prerequisite_course_id:
        raise ValueError('A course cannot be a prerequisite of itself')

@db.event.listens_for(Enrolled, 'after_update')
def update_total_credits_after_completion(mapper, connection, target):
    student = db.session.get(Student, target.student_id)
    if target.status == EnrollmentStatus.completed:
        student.total_credits = student.get_completed_credits() + student.get_current_enrolled_credits()
    elif target.status == EnrollmentStatus.enrolled:
        student.total_credits = student.get_completed_credits() + student.get_current_enrolled_credits()