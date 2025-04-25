from web import create_app
from web.models import db, Student, StudentStatus, Course, Prerequisite
from datetime import date


def main():
    # Initialize Flask app and test client
    app = create_app()
    app.testing = True
    client = app.test_client()

    # Set up test database with sample data
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create sample student
        student = Student(
            student_id='1', first_name='John', last_name='Doe',
            date_of_birth=date(2000, 1, 1), major='Computer Science',
            email='john.doe@university.edu', enrollment_date=date.today()
        )
        student.status = StudentStatus.active
        db.session.add(student)
        # Create courses
        prereq_course = Course(
            course_id='1', course_code='CS101', course_name='Intro Programming',
            description='Introduction to programming', credits=3, department='CS'
        )
        main_course = Course(
            course_id='2', course_code='CS201', course_name='Data Structures',
            description='Study of data structures', credits=4, department='CS'
        )
        db.session.add_all([prereq_course, main_course])
        db.session.commit()
        # Create prerequisite relationship
        prereq_rel = Prerequisite(course_id='2', prerequisite_course_id='1')
        db.session.add(prereq_rel)
        db.session.commit()

    # Test unauthenticated access
    response = client.get('/prerequisites/1')
    print('Unauthenticated access status:', response.status_code)
    print('Redirect location:', response.headers.get('Location'))

    # Perform login as student with ID 1
    login_response = client.post(
        '/login',
        data={'user_id': '1', 'user_type': 'student'},
        follow_redirects=True
    )
    print('Login status:', login_response.status_code)

    # Test authenticated access to prerequisites of course 2 (has prerequisites)
    response2 = client.get('/prerequisites/2', follow_redirects=True)
    print('Authenticated access status (course 2):', response2.status_code)
    print('Page content snippet:', response2.data.decode(errors='ignore')[:200])

    # Test authenticated access to prerequisites of course 1 (no prerequisites)
    response3 = client.get('/prerequisites/1', follow_redirects=True)
    print('Authenticated access status (course 1):', response3.status_code)
    print('Page content snippet for course 1:', response3.data.decode(errors='ignore')[:200])


if __name__ == '__main__':
    main() 