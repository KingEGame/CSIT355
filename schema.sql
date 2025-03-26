-- Part 1: Database Design

-- University Course Management System Schema

-- Drop tables if they exist
DROP TABLE IF EXISTS Enrollment;
DROP TABLE IF EXISTS Teaching;
DROP TABLE IF EXISTS Schedule;
DROP TABLE IF EXISTS Prerequisites;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Professor;
DROP TABLE IF EXISTS Student;

-- Create custom types (MySQL doesn't support ENUM creation separately, so we'll use ENUM directly in tables)

-- Student table
CREATE TABLE Student (
    student_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE,
    major VARCHAR(50),
    enrollment_date DATE NOT NULL,
    status ENUM('active', 'inactive', 'graduated') DEFAULT 'active'
);

-- Professor table
CREATE TABLE Professor (
    professor_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    hire_date DATE NOT NULL,
    status ENUM('active', 'inactive', 'retired') DEFAULT 'active'
);

-- Course table
CREATE TABLE Course (
    course_id VARCHAR(10) PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    credits INT NOT NULL CHECK (credits > 0),
    department VARCHAR(50),
    level ENUM('undergraduate', 'graduate', 'doctoral') NOT NULL,
    status VARCHAR(10) DEFAULT 'active',
    CONSTRAINT valid_course_code CHECK (course_code REGEXP '^[A-Z]{2,4}[0-9]{3,4}$')
);

-- Prerequisites table
CREATE TABLE Prerequisites (
    course_id VARCHAR(10),
    prerequisite_id VARCHAR(10),
    PRIMARY KEY (course_id, prerequisite_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id),
    FOREIGN KEY (prerequisite_id) REFERENCES Course(course_id),
    CONSTRAINT no_self_prerequisite CHECK (course_id != prerequisite_id)
);

-- Schedule table
CREATE TABLE Schedule (
    schedule_id VARCHAR(10) PRIMARY KEY,
    course_id VARCHAR(10),
    semester VARCHAR(20) NOT NULL,
    academic_year INT NOT NULL,
    meeting_days VARCHAR(20) NOT NULL CHECK (meeting_days REGEXP '^[MTWRF]+$'),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_number VARCHAR(20),
    building VARCHAR(50),
    max_capacity INT NOT NULL DEFAULT 25,
    current_enrollment INT DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

-- Teaching table
CREATE TABLE Teaching (
    teaching_id VARCHAR(10) PRIMARY KEY,
    professor_id VARCHAR(10),
    schedule_id VARCHAR(10),
    FOREIGN KEY (professor_id) REFERENCES Professor(professor_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id)
);

-- Enrollment table
CREATE TABLE Enrollment (
    enrollment_id VARCHAR(10) PRIMARY KEY,
    student_id VARCHAR(10),
    schedule_id VARCHAR(10),
    enrollment_date DATE NOT NULL,
    grade ENUM('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W', 'I') DEFAULT NULL,
    status ENUM('enrolled', 'dropped', 'completed', 'withdrawn') DEFAULT 'enrolled',
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id),
    UNIQUE(student_id, schedule_id)
);

-- Clear existing data from Prerequisites table first (only for specific courses)
DELETE FROM Prerequisites 
WHERE course_id IN ('CSE101', 'CSE232', 'CSE331', 'CSE435', 'CSE480')
   OR prerequisite_id IN ('CSE101', 'CSE232', 'CSE331', 'CSE435', 'CSE480');

-- Clear existing data from Course table (only specific courses)
DELETE FROM Course 
WHERE course_id IN ('CSE101', 'CSE232', 'CSE331', 'CSE435', 'CSE480');

-- Insert sample CS courses
INSERT INTO Course (course_id, course_code, course_name, description, credits, department, level) VALUES
    ('CSE101', 'CSE101', 'Introduction to Programming', 'Basic programming concepts and problem-solving techniques', 3, 'Computer Science', 'undergraduate'),
    ('CSE232', 'CSE232', 'Introduction to Programming Languages', 'Study of programming language concepts and paradigms', 3, 'Computer Science', 'undergraduate'),
    ('CSE331', 'CSE331', 'Algorithms and Data Structures', 'Design and analysis of algorithms and data structures', 3, 'Computer Science', 'undergraduate'),
    ('CSE435', 'CSE435', 'Software Engineering', 'Software development methodologies and practices', 3, 'Computer Science', 'undergraduate'),
    ('CSE480', 'CSE480', 'Database Systems', 'Design and implementation of database systems', 3, 'Computer Science', 'undergraduate');

DELIMITER //
END //
DELIMITER ;

-- Part 2: Database Application

-- Create view for schedule conflicts
CREATE OR REPLACE VIEW schedule_conflicts AS
SELECT 
    e.student_id,
    s2.schedule_id as new_schedule_id,
    COUNT(*) > 0 as has_conflict
FROM Enrollment e
JOIN Schedule s1 ON e.schedule_id = s1.schedule_id
JOIN Schedule s2 ON s1.semester = s2.semester 
    AND s1.academic_year = s2.academic_year
    AND s1.meeting_days REGEXP CONCAT('[', s2.meeting_days, ']')
    AND s1.start_time <= s2.end_time 
    AND s2.start_time <= s1.end_time
WHERE e.status = 'enrolled'
GROUP BY e.student_id, s2.schedule_id;

-- Create view for prerequisites check
CREATE OR REPLACE VIEW prerequisites_check AS
SELECT 
    e.student_id,
    p.course_id,
    NOT EXISTS (
        SELECT 1
        FROM Prerequisites prereq
        WHERE prereq.course_id = p.course_id
        AND NOT EXISTS (
            SELECT 1
            FROM Enrollment completed
            JOIN Schedule s ON completed.schedule_id = s.schedule_id
            WHERE completed.student_id = e.student_id
            AND s.course_id = prereq.prerequisite_id
            AND completed.status = 'completed'
            AND completed.grade NOT IN ('F', 'W', 'I')
        )
    ) as meets_prerequisites
FROM Enrollment e
CROSS JOIN Prerequisites p
GROUP BY e.student_id, p.course_id;

-- Create view for valid schedule times
CREATE OR REPLACE VIEW valid_schedule_times AS
SELECT 
    schedule_id,
    CASE 
        WHEN start_time >= '08:00:00' 
        AND end_time <= '22:00:00' 
        AND start_time < end_time 
        THEN TRUE 
        ELSE FALSE 
    END as is_valid_time
FROM Schedule;

-- Example queries to use instead of procedures:
-- To check schedule conflicts:
-- SELECT has_conflict FROM schedule_conflicts WHERE student_id = ? AND new_schedule_id = ?;

-- To check prerequisites:
-- SELECT meets_prerequisites FROM prerequisites_check WHERE student_id = ? AND course_id = ?;

-- To check valid schedule times:
-- SELECT is_valid_time FROM valid_schedule_times WHERE schedule_id = ?;

-- Check for schedule conflicts
SELECT has_conflict 
FROM schedule_conflicts 
WHERE student_id = 'STUDENT1' AND new_schedule_id = 'SCHEDULE1';

-- Check prerequisites
SELECT meets_prerequisites 
FROM prerequisites_check 
WHERE student_id = 'STUDENT1' AND course_id = 'COURSE1';

-- Check if schedule time is valid
SELECT is_valid_time 
FROM valid_schedule_times 
WHERE schedule_id = 'SCHEDULE1';