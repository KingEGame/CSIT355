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
    CONSTRAINT chk_student_dob CHECK (date_of_birth <= CURRENT_DATE - INTERVAL 16 YEAR),
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
    FOREIGN KEY (prerequisite_course_id) REFERENCES Courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT no_self_prerequisite CHECK (course_id != prerequisite_course_id)
);

-- Create Schedule table 
CREATE TABLE Schedule (
    schedule_id VARCHAR(10) PRIMARY KEY,
    course_id VARCHAR(10) NOT NULL,
    semester ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    meeting_days VARCHAR(10) NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    current_enrollment INT DEFAULT 0,
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