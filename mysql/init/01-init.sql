-- Create Database and Use It
CREATE DATABASE IF NOT EXISTS csit_555;
USE csit_555;

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS teaching;
DROP TABLE IF EXISTS enrolled;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS prerequisite;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS professor;
DROP TABLE IF EXISTS student;

-- Create student table 
CREATE TABLE student (
    student_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    major VARCHAR(50) NOT NULL,
    status ENUM('active', 'inactive', 'graduated', 'suspended', 'on_leave') DEFAULT 'active',
    level ENUM('undergraduate', 'graduate', 'phd') DEFAULT 'undergraduate',
    enrollment_date DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    INDEX idx_student_email (email),
    INDEX idx_student_status (status),
    CONSTRAINT chk_student_email CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);

-- Create professor table 
CREATE TABLE professor (
    professor_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    office_number VARCHAR(20),
    phone VARCHAR(20),
    INDEX idx_professor_email (email),
    INDEX idx_professor_department (department),
    CONSTRAINT chk_professor_email CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);

-- Create courses table 
CREATE TABLE courses (
    course_id VARCHAR(10) PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    credits INT NOT NULL,
    department VARCHAR(50) NOT NULL,
    level ENUM('undergraduate', 'graduate', 'phd') DEFAULT 'undergraduate',
    max_capacity INT DEFAULT 30,
    INDEX idx_course_code (course_code),
    INDEX idx_course_department (department),
    CONSTRAINT chk_course_credits CHECK (credits BETWEEN 1 AND 6),
    CONSTRAINT chk_course_capacity CHECK (max_capacity BETWEEN 5 AND 300)
);

-- Create prerequisite table 
CREATE TABLE prerequisite (
    prerequisite_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    prerequisite_course_id VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_prerequisite (course_id, prerequisite_course_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (prerequisite_course_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create schedule table 
CREATE TABLE schedule (
    schedule_id VARCHAR(10) PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    semester ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    meeting_days VARCHAR(10) NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    academic_year INT NOT NULL,
    max_enrollment INT NOT NULL,
    current_enrollment INT DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_schedule_semester (semester, academic_year),
    CONSTRAINT chk_schedule_time CHECK (start_time < end_time),
    CONSTRAINT chk_schedule_days CHECK (meeting_days REGEXP '^[MTWRF]+$'),
    CONSTRAINT chk_current_enrollment CHECK (current_enrollment <= max_enrollment)
);

-- Create enrolled table 
CREATE TABLE enrolled (
    enrollment_id VARCHAR(10) PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL,
    schedule_id VARCHAR(10) NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    grade VARCHAR(2),
    status ENUM('enrolled', 'dropped', 'withdrawn', 'completed') DEFAULT 'enrolled',
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, schedule_id),
    INDEX idx_enrollment_status (status),
    CONSTRAINT chk_grade CHECK (grade IN ('A+','A','A-','B+','B','B-','C+','C','C-','D+','D','F','W','I'))
);

-- Create teaching table
CREATE TABLE teaching (
    teaching_id VARCHAR(10) PRIMARY KEY,
    professor_id VARCHAR(10) NOT NULL,
    schedule_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (professor_id) REFERENCES professor(professor_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_teaching_assignment (professor_id, schedule_id)
);

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS after_enrollment_insert;
DROP TRIGGER IF EXISTS after_enrollment_delete;
DROP TRIGGER IF EXISTS before_prerequisite_insert;
DROP TRIGGER IF EXISTS before_prerequisite_update;
DROP TRIGGER IF EXISTS before_schedule_insert;
DROP TRIGGER IF EXISTS before_schedule_update;
DROP TRIGGER IF EXISTS before_student_insert;
DROP TRIGGER IF EXISTS before_student_update;

-- Create triggers to maintain enrollment counts
DELIMITER //

CREATE TRIGGER after_enrollment_insert
AFTER INSERT ON enrolled
FOR EACH ROW
BEGIN
    UPDATE schedule 
    SET current_enrollment = current_enrollment + 1
    WHERE schedule_id = NEW.schedule_id;
END//

CREATE TRIGGER after_enrollment_delete
AFTER DELETE ON enrolled
FOR EACH ROW
BEGIN
    UPDATE schedule 
    SET current_enrollment = current_enrollment - 1
    WHERE schedule_id = OLD.schedule_id;
END//

-- Add trigger to prevent self-prerequisites
CREATE TRIGGER before_prerequisite_insert
BEFORE INSERT ON prerequisite
FOR EACH ROW
BEGIN
    IF NEW.course_id = NEW.prerequisite_course_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A course cannot be a prerequisite of itself';
    END IF;
END//

CREATE TRIGGER before_prerequisite_update
BEFORE UPDATE ON prerequisite
FOR EACH ROW
BEGIN
    IF NEW.course_id = NEW.prerequisite_course_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A course cannot be a prerequisite of itself';
    END IF;
END//

-- Add triggers to enforce academic_year >= current year
CREATE TRIGGER before_schedule_insert
BEFORE INSERT ON schedule
FOR EACH ROW
BEGIN
    IF NEW.academic_year < YEAR(CURRENT_DATE) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Academic year must be greater than or equal to the current year';
    END IF;
END//

CREATE TRIGGER before_schedule_update
BEFORE UPDATE ON schedule
FOR EACH ROW
BEGIN
    IF NEW.academic_year < YEAR(CURRENT_DATE) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Academic year must be greater than or equal to the current year';
    END IF;
END//

-- Add triggers to enforce minimum age of 16 for student
CREATE TRIGGER before_student_insert
BEFORE INSERT ON student
FOR EACH ROW
BEGIN
    IF NEW.date_of_birth > CURRENT_DATE - INTERVAL 16 YEAR THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student must be at least 16 years old';
    END IF;
END//

CREATE TRIGGER before_student_update
BEFORE UPDATE ON student
FOR EACH ROW
BEGIN
    IF NEW.date_of_birth > CURRENT_DATE - INTERVAL 16 YEAR THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student must be at least 16 years old';
    END IF;
END//

DELIMITER ;
