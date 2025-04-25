from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, EmailField, TextAreaField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, EqualTo, Regexp, NumberRange
from web.models import Student, StudentStatus, CourseLevel, Major, Professor, Department, Course
import re

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required"),
        Length(min=2, max=50, message="First name must be between 2 and 50 characters")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message="Last name is required"),
        Length(min=2, max=50, message="Last name must be between 2 and 50 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email must be less than 120 characters")
    ])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])

    def validate_new_password(self, field):
        if self.current_password.data and not field.data:
            raise ValidationError("New password is required when changing password")
        if field.data and not self.current_password.data:
            raise ValidationError("Current password is required to set a new password")

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    major = SelectField('Major', validators=[DataRequired()])
    level = SelectField('Level', validators=[DataRequired()])
    status = SelectField('Status', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.major.choices = [(m.name, m.value) for m in Major]
        self.level.choices = [(l.name, l.value) for l in CourseLevel]
        self.status.choices = [(s.name, s.value) for s in StudentStatus]

    def validate_email(self, field):
        student = Student.query.filter_by(email=field.data).first()
        if student:
            if not hasattr(self, 'student') or student.id != self.student.id:
                raise ValidationError('Email already registered.')

class ProfessorForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    department = SelectField('Department', validators=[DataRequired()])
    office_location = StringField('Office Location', validators=[
        DataRequired(),
        Length(max=50, message='Office location must be less than 50 characters')
    ])
    office_hours = TextAreaField('Office Hours', validators=[
        DataRequired(),
        Length(max=200, message='Office hours description must be less than 200 characters')
    ])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(max=20, message='Phone number must be less than 20 characters')
    ])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave')
    ], validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(ProfessorForm, self).__init__(*args, **kwargs)
        self.department.choices = [(d.name, d.value) for d in Department]

    def validate_email(self, field):
        professor = Professor.query.filter_by(email=field.data).first()
        if professor:
            if not hasattr(self, 'professor') or professor.id != self.professor.id:
                raise ValidationError('Email already registered.')

class CourseForm(FlaskForm):
    code = StringField('Course Code', validators=[
        DataRequired(),
        Length(min=2, max=10),
        Regexp(r'^[A-Z]{2,4}\d{3,4}$', message='Course code must be 2-4 letters followed by 3-4 numbers (e.g., CS355)')
    ])
    name = StringField('Course Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ])
    department = SelectField('Department', validators=[DataRequired()], coerce=str)
    level = SelectField('Level', validators=[DataRequired()], coerce=str)
    credits = IntegerField('Credits', validators=[
        DataRequired(),
        NumberRange(min=1, max=6, message='Credits must be between 1 and 6')
    ])
    prerequisites = StringField('Prerequisites', validators=[Optional()])
    is_active = BooleanField('Active')

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.department.choices = [(dept.name, dept.value) for dept in Department]
        self.level.choices = [(level.name, level.value) for level in CourseLevel]

    def validate_prerequisites(self, field):
        if not field.data:
            return
        
        prereq_codes = [code.strip() for code in field.data.split(',')]
        for code in prereq_codes:
            if not re.match(r'^[A-Z]{2,4}\d{3,4}$', code):
                raise ValidationError('Invalid course code format in prerequisites')
            
            # Check if prerequisite course exists
            prereq_course = Course.query.filter_by(code=code).first()
            if not prereq_course:
                raise ValidationError(f'Prerequisite course {code} does not exist') 