import argparse
from sql_connection import DatabaseConnection
from datetime import datetime
import sys

def init_database():
    """Initialize the database schema."""
    db = DatabaseConnection()
    try:
        with open('schema.sql', 'r') as f:
            schema = f.read()
            db.execute_script(schema)
        print("Successfully initialized database.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

def load_test_data():
    """Load test data into the database."""
    db = DatabaseConnection()
    try:
        with open('test_data.sql', 'r') as f:
            test_data = f.read()
            db.execute_script(test_data)
        print("Successfully loaded test data into database.")
    except Exception as e:
        print(f"Error loading test data: {e}")
    finally:
        db.close()

def reset_database():
    """Reset the database by reinitializing the schema."""
    init_database()
    print("Successfully reset database.")

def print_menu():
    print("\nMSU Course Management System")
    print("L - List all courses")
    print("E - Enroll in a course")
    print("W - Withdraw from a course")
    print("S - Search courses")
    print("M - My Classes")
    print("P - Prerequisites")
    print("T - Teaching Professor")
    print("X - Exit")

def create_new_student(db):
    print("\nNew Student Registration")
    student_id = input("Enter student ID: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    date_of_birth = input("Enter date of birth (YYYY-MM-DD): ")
    major = input("Enter major: ")

    if db.create_student(student_id, first_name, last_name, email, date_of_birth, major):
        print("Student created successfully!")
    else:
        print("Error creating student.")
    return student_id

def display_courses(courses):
    if not courses:
        print("No courses found.")
        return

    print("\nCourse List:")
    print("-" * 100)
    print(f"{'Course ID':<10} {'Course Name':<30} {'Semester':<10} {'Days':<10} {'Time':<15} {'Location':<20} {'Professor':<20}")
    print("-" * 100)

    for course in courses:
        print(f"{course[0]:<10} {course[1]:<30} {course[2]:<10} {course[4]:<10} "
              f"{course[5].strftime('%H:%M')}-{course[6].strftime('%H:%M')} "
              f"{course[8]} {course[7]:<15} {course[9]} {course[10]:<20}")
    print("-" * 100)

def main():
    parser = argparse.ArgumentParser(description='MSU Course Management System')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode')
    parser.add_argument('--init-db', action='store_true',
                      help='Initialize database schema')
    parser.add_argument('--reset-db', action='store_true',
                      help='Reset database')
    parser.add_argument('--load-test-data', action='store_true',
                      help='Load test data into database')

    args = parser.parse_args()

    # Handle database operations
    if args.init_db:
        init_database()
        return
    elif args.reset_db:
        reset_database()
        return
    elif args.load_test_data:
        load_test_data()
        return

    # Initialize database connection
    db = DatabaseConnection()
    current_student = None

    try:
        while True:
            if not current_student:
                student_id = input("\nEnter your student ID (or -1 to create new student): ")
                if student_id == "-1":
                    current_student = create_new_student(db)
                else:
                    student = db.get_student(student_id)
                    if student:
                        current_student = student_id
                        print(f"\nWelcome back, {student[1]} {student[2]}!")
                    else:
                        print("Student not found.")
                        continue

            print_menu()
            choice = input("\nEnter your choice: ").upper()

            if choice == 'L':
                courses = db.list_all_courses()
                display_courses(courses)

            elif choice == 'E':
                courses = db.list_all_courses()
                display_courses(courses)
                schedule_id = input("\nEnter schedule ID to enroll: ")
                success, message = db.enroll_student(current_student, schedule_id)
                print(message)

            elif choice == 'W':
                courses = db.get_student_courses(current_student)
                display_courses(courses)
                schedule_id = input("\nEnter schedule ID to withdraw: ")
                success, message = db.withdraw_student(current_student, schedule_id)
                print(message)

            elif choice == 'S':
                search_term = input("\nEnter search term: ")
                courses = db.search_courses(search_term)
                display_courses(courses)

            elif choice == 'M':
                courses = db.get_student_courses(current_student)
                display_courses(courses)

            elif choice == 'P':
                course_id = input("\nEnter course ID: ")
                prerequisites = db.get_course_prerequisites(course_id)
                if prerequisites:
                    print("\nPrerequisites:")
                    for prereq in prerequisites:
                        print(f"- {prereq[0]}: {prereq[1]}")
                else:
                    print("No prerequisites found.")

            elif choice == 'T':
                professors = db.get_professor_courses()
                if professors:
                    current_prof = None
                    print("\nProfessor Information:")
                    print("-" * 80)
                    for prof in professors:
                        if current_prof != prof[0]:
                            current_prof = prof[0]
                            print(f"\nProfessor: {prof[2]} {prof[3]}")
                            print(f"Department: {prof[4]}")
                            print("Courses:")
                        print(f"  - {prof[5]}: {prof[6]}")
                else:
                    print("No professor information found.")

            elif choice == 'X':
                print("\nThank you for using MSU Course Management System!")
                break

            else:
                print("\nInvalid choice. Please try again.")

    except Exception as e:
        if args.debug:
            import traceback
            print(f"An error occurred: {e}")
            print("Traceback:")
            traceback.print_exc()
        else:
            print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()