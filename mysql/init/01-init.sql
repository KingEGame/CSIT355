-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS csit_555;

-- Use the database
USE csit_555;

-- Create a user if it doesn't exist and grant privileges
CREATE USER IF NOT EXISTS 'db'@'%' IDENTIFIED BY 'csit_555';
GRANT ALL PRIVILEGES ON csit_555.* TO 'db'@'%';
FLUSH PRIVILEGES;

-- Import schema
-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS Teaching;
DROP TABLE IF EXISTS Enrolled;
DROP TABLE IF EXISTS Schedule;
DROP TABLE IF EXISTS Prerequisite;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Professor;
DROP TABLE IF EXISTS Student;

-- Create Student table 
CREATE TABLE Student (
    student_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    major VARCHAR(50) NOT NULL,
    status ENUM('active', 'inactive', 'graduated', 'suspended', 'on_leave') DEFAULT 'active',
    enrollment_date DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    INDEX idx_student_email (email),
    INDEX idx_student_status (status),
    CONSTRAINT chk_student_email CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);

-- Create Professor table 
CREATE TABLE Professor (
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

-- Create Courses table 
CREATE TABLE Courses (
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

-- Create Prerequisite table 
CREATE TABLE Prerequisite (
    prerequisite_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    prerequisite_course_id VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_prerequisite (course_id, prerequisite_course_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (prerequisite_course_id) REFERENCES Courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Add trigger to prevent self-prerequisites
DELIMITER //

CREATE TRIGGER before_prerequisite_insert
BEFORE INSERT ON Prerequisite
FOR EACH ROW
BEGIN
    IF NEW.course_id = NEW.prerequisite_course_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A course cannot be a prerequisite of itself';
    END IF;
END//

CREATE TRIGGER before_prerequisite_update
BEFORE UPDATE ON Prerequisite
FOR EACH ROW
BEGIN
    IF NEW.course_id = NEW.prerequisite_course_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A course cannot be a prerequisite of itself';
    END IF;
END//

DELIMITER ;

-- Create Schedule table 
CREATE TABLE Schedule (
    schedule_id VARCHAR(10) PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    semester ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    academic_year INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    meeting_days VARCHAR(10) NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    current_enrollment INT DEFAULT 0,
    max_enrollment INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_schedule_semester (semester, academic_year),
    CONSTRAINT chk_schedule_time CHECK (start_time < end_time),
    CONSTRAINT chk_schedule_days CHECK (meeting_days REGEXP '^[MTWRF]+$'),
    CONSTRAINT chk_current_enrollment CHECK (current_enrollment <= max_enrollment),
    CONSTRAINT chk_academic_year CHECK (academic_year >= YEAR(CURRENT_DATE))
);

-- Create Enrolled table 
CREATE TABLE Enrolled (
    enrollment_id VARCHAR(10) PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL,
    schedule_id VARCHAR(10) NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    grade VARCHAR(2),
    status ENUM('enrolled', 'dropped', 'withdrawn', 'completed') DEFAULT 'enrolled',
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, schedule_id),
    INDEX idx_enrollment_status (status),
    CONSTRAINT chk_grade CHECK (grade IN ('A+','A','A-','B+','B','B-','C+','C','C-','D+','D','F','W','I'))
);

-- Create Teaching table
CREATE TABLE Teaching (
    teaching_id VARCHAR(10) PRIMARY KEY,
    professor_id VARCHAR(10) NOT NULL,
    schedule_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (professor_id) REFERENCES Professor(professor_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY unique_teaching_assignment (professor_id, schedule_id)
);

-- Create triggers to maintain enrollment counts
DELIMITER //

CREATE TRIGGER after_enrollment_insert
AFTER INSERT ON Enrolled
FOR EACH ROW
BEGIN
    UPDATE Schedule 
    SET current_enrollment = current_enrollment + 1
    WHERE schedule_id = NEW.schedule_id;
END//

CREATE TRIGGER after_enrollment_delete
AFTER DELETE ON Enrolled
FOR EACH ROW
BEGIN
    UPDATE Schedule 
    SET current_enrollment = current_enrollment - 1
    WHERE schedule_id = OLD.schedule_id;
END//

DELIMITER ;

-- Import test data
-- Insert test data for Student table
INSERT INTO Student (student_id, first_name, last_name, date_of_birth, major, enrollment_date, email) VALUES
('S001', 'John', 'Doe', '2000-05-15', 'Computer Science', '2020-09-01', 'john.doe@university.edu'),
('S002', 'Jane', 'Smith', '2001-03-22', 'Mathematics', '2021-01-15', 'jane.smith@university.edu'),
('S003', 'Michael', 'Johnson', '2000-11-30', 'Physics', '2020-09-01', 'michael.j@university.edu');

-- Insert test data for Professor table
INSERT INTO Professor (professor_id, first_name, last_name, department, hire_date, email, office_number, phone) VALUES
('P001', 'Robert', 'Wilson', 'Computer Science', '2015-08-01', 'r.wilson@university.edu', 'CS-101', '555-0101'),
('P002', 'Sarah', 'Brown', 'Mathematics', '2018-01-15', 's.brown@university.edu', 'MA-201', '555-0202'),
('P003', 'David', 'Lee', 'Physics', '2010-09-01', 'd.lee@university.edu', 'PH-301', '555-0303');

-- Insert test data for Courses table
INSERT INTO Courses (course_id, course_code, course_name, description, credits, department, max_capacity) VALUES
('C001', 'CS101', 'Introduction to Programming', 'Basic programming concepts', 3, 'Computer Science', 50),
('C002', 'CS102', 'Data Structures', 'Fundamental data structures', 3, 'Computer Science', 40),
('C003', 'MATH201', 'Calculus I', 'Introduction to calculus', 4, 'Mathematics', 45);

-- Insert test data for Schedule table
INSERT INTO Schedule (schedule_id, course_id, semester, academic_year, start_time, end_time, meeting_days, room_number, max_enrollment) VALUES
('SCH001', 'C001', 'Fall', 2023, '09:00:00', '10:30:00', 'MWF', 'R101', 50),
('SCH002', 'C002', 'Spring', 2024, '11:00:00', '12:30:00', 'TR', 'R102', 40),
('SCH003', 'C003', 'Fall', 2023, '14:00:00', '15:30:00', 'MWF', 'R103', 45);

-- Insert test data for Teaching table
INSERT INTO Teaching (teaching_id, professor_id, schedule_id) VALUES
('T001', 'P001', 'SCH001'),
('T002', 'P001', 'SCH002'),
('T003', 'P002', 'SCH003');

-- Insert test data for Prerequisite table
INSERT INTO Prerequisite (course_id, prerequisite_course_id) VALUES
('C002', 'C001');

-- Insert test data for Enrolled table
INSERT INTO Enrolled (enrollment_id, student_id, schedule_id, enrollment_date, grade, status) VALUES
('E001', 'S001', 'SCH001', '2023-08-25', NULL, 'enrolled'),
('E002', 'S002', 'SCH001', '2023-08-26', NULL, 'enrolled'),
('E003', 'S003', 'SCH002', '2023-08-25', NULL, 'enrolled'); 