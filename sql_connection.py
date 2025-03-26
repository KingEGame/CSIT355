import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        try:
            # Parse DATABASE_URL from environment
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                raise ValueError("DATABASE_URL not set in environment")
            
            # mysql://username:password@localhost/course_management
            db_url = db_url.replace('mysql://', '')
            credentials, db = db_url.split('@')
            username, password = credentials.split(':')
            host, database = db.split('/')

            self.conn = mysql.connector.connect(
                host=host,
                user=username,
                password=password,
                database=database
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def get_student(self, student_id):
        self.cur.execute("""
            SELECT * FROM Student WHERE student_id = %s
        """, (student_id,))
        return self.cur.fetchone()

    def create_student(self, student_id, first_name, last_name, email, date_of_birth, major):
        try:
            self.cur.execute("""
                INSERT INTO Student (student_id, first_name, last_name, email, date_of_birth, major, enrollment_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (student_id, first_name, last_name, email, date_of_birth, major, datetime.now().date()))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating student: {e}")
            return False

    def list_all_courses(self):
        self.cur.execute("""
            SELECT c.course_id, c.course_name, s.semester, s.academic_year, 
                   s.meeting_days, s.start_time, s.end_time, s.room_number, s.building,
                   p.first_name, p.last_name, p.department
            FROM Course c
            JOIN Schedule s ON c.course_id = s.course_id
            JOIN Teaching t ON s.schedule_id = t.schedule_id
            JOIN Professor p ON t.professor_id = p.professor_id
            ORDER BY c.course_id
        """)
        return self.cur.fetchall()

    def enroll_student(self, student_id, schedule_id):
        try:
            # Check prerequisites
            self.cur.execute("""
                SELECT check_prerequisites(%s, c.course_id)
                FROM Schedule s
                JOIN Course c ON s.course_id = c.course_id
                WHERE s.schedule_id = %s
            """, (student_id, schedule_id))
            if not self.cur.fetchone()[0]:
                return False, "Prerequisites not met"

            # Check schedule conflict
            self.cur.execute("""
                SELECT check_schedule_conflict(%s, %s)
            """, (student_id, schedule_id))
            if self.cur.fetchone()[0]:
                return False, "Schedule conflict detected"

            # Check capacity
            self.cur.execute("""
                SELECT current_enrollment, max_capacity
                FROM Schedule
                WHERE schedule_id = %s
            """, (schedule_id,))
            current, max_cap = self.cur.fetchone()
            if current >= max_cap:
                return False, "Course is full"

            # Enroll student
            self.cur.execute("""
                INSERT INTO Enrollment (enrollment_id, student_id, schedule_id, enrollment_date)
                VALUES (%s, %s, %s, %s)
            """, (f"ENR{datetime.now().strftime('%Y%m%d%H%M%S')}", student_id, schedule_id, datetime.now().date()))

            # Update current enrollment
            self.cur.execute("""
                UPDATE Schedule
                SET current_enrollment = current_enrollment + 1
                WHERE schedule_id = %s
            """, (schedule_id,))

            self.conn.commit()
            return True, "Enrollment successful"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error enrolling student: {e}"

    def withdraw_student(self, student_id, schedule_id):
        try:
            self.cur.execute("""
                DELETE FROM Enrollment
                WHERE student_id = %s AND schedule_id = %s AND status = 'enrolled'
            """, (student_id, schedule_id))

            # Update current enrollment
            self.cur.execute("""
                UPDATE Schedule
                SET current_enrollment = current_enrollment - 1
                WHERE schedule_id = %s
            """, (schedule_id,))

            self.conn.commit()
            return True, "Withdrawal successful"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error withdrawing student: {e}"

    def search_courses(self, search_term):
        self.cur.execute("""
            SELECT c.course_id, c.course_name, s.semester, s.academic_year, 
                   s.meeting_days, s.start_time, s.end_time, s.room_number, s.building,
                   p.first_name, p.last_name, p.department
            FROM Course c
            JOIN Schedule s ON c.course_id = s.course_id
            JOIN Teaching t ON s.schedule_id = t.schedule_id
            JOIN Professor p ON t.professor_id = p.professor_id
            WHERE LOWER(c.course_name) LIKE LOWER(%s)
            ORDER BY c.course_id
        """, (f"%{search_term}%",))
        return self.cur.fetchall()

    def get_student_courses(self, student_id):
        self.cur.execute("""
            SELECT c.course_id, c.course_name, s.semester, s.academic_year, 
                   s.meeting_days, s.start_time, s.end_time, s.room_number, s.building,
                   p.first_name, p.last_name, p.department
            FROM Course c
            JOIN Schedule s ON c.course_id = s.course_id
            JOIN Teaching t ON s.schedule_id = t.schedule_id
            JOIN Professor p ON t.professor_id = p.professor_id
            JOIN Enrollment e ON s.schedule_id = e.schedule_id
            WHERE e.student_id = %s AND e.status = 'enrolled'
            ORDER BY c.course_id
        """, (student_id,))
        return self.cur.fetchall()

    def get_course_prerequisites(self, course_id):
        self.cur.execute("""
            SELECT c.course_id, c.course_name, c.description
            FROM Course c
            JOIN Prerequisites p ON c.course_id = p.prerequisite_id
            WHERE p.course_id = %s
            ORDER BY c.course_id
        """, (course_id,))
        return self.cur.fetchall()

    def get_professor_courses(self):
        self.cur.execute("""
            SELECT p.professor_id, p.first_name, p.last_name, p.department,
                   c.course_id, c.course_name
            FROM Professor p
            JOIN Teaching t ON p.professor_id = t.professor_id
            JOIN Schedule s ON t.schedule_id = s.schedule_id
            JOIN Course c ON s.course_id = c.course_id
            ORDER BY p.last_name, p.first_name, c.course_id
        """)
        return self.cur.fetchall()

