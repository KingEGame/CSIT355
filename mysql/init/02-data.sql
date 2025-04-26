-- Test data for student table
INSERT INTO student (student_id, first_name, last_name, date_of_birth, major, status, level, enrollment_date, email) VALUES
('ST001', 'John', 'Smith', '2000-05-15', 'Computer Science', 'active', 'undergraduate', '2020-09-01', 'john.smith@university.edu'),
('ST002', 'Emma', 'Johnson', '1998-03-22', 'Mathematics', 'active', 'graduate', '2021-01-15', 'emma.j@university.edu'),
('ST003', 'Michael', 'Brown', '1995-11-30', 'Physics', 'active', 'phd', '2019-09-01', 'michael.b@university.edu'),
('ST004', 'Sarah', 'Davis', '2000-07-18', 'Chemistry', 'graduated', 'undergraduate', '2019-09-01', 'sarah.d@university.edu'),
('ST005', 'David', 'Wilson', '1997-09-25', 'Computer Science', 'active', 'graduate', '2021-09-01', 'david.w@university.edu');

-- Test data for professor table
INSERT INTO professor (professor_id, first_name, last_name, department, hire_date, email, office_number, phone) VALUES
('PR001', 'Robert', 'Anderson', 'Computer Science', '2015-08-15', 'r.anderson@university.edu', 'CS-201', '555-0401'),
('PR002', 'Jennifer', 'Martinez', 'Mathematics', '2012-01-10', 'j.martinez@university.edu', 'MA-301', '555-0402'),
('PR003', 'William', 'Taylor', 'Physics', '2010-09-01', 'w.taylor@university.edu', 'PH-401', '555-0403'),
('PR004', 'Elizabeth', 'Thomas', 'Chemistry', '2018-06-20', 'e.thomas@university.edu', 'CH-501', '555-0404');

-- Test data for courses table
INSERT INTO courses (course_id, course_code, course_name, description, credits, department, level, max_capacity) VALUES
('CRS001', 'CS101', 'Introduction to Programming', 'Basic concepts of programming using Python', 3, 'Computer Science', 'undergraduate', 30),
('CRS002', 'CS201', 'Data Structures', 'Advanced programming concepts and data structures', 4, 'Computer Science', 'undergraduate', 25),
('CRS003', 'MATH201', 'Calculus I', 'Limits, derivatives, and basic integration', 4, 'Mathematics', 'undergraduate', 35),
('CRS004', 'PHYS101', 'General Physics', 'Introduction to mechanics and thermodynamics', 4, 'Physics', 'undergraduate', 30),
('CRS005', 'CHEM101', 'General Chemistry', 'Basic principles of chemistry', 4, 'Chemistry', 'undergraduate', 30);

-- Test data for prerequisite table
INSERT INTO prerequisite (course_id, prerequisite_course_id) VALUES
('CRS002', 'CRS001'), -- CS201 requires CS101
('CRS004', 'CRS003'); -- PHYS101 requires MATH201

-- Test data for schedule table
INSERT INTO schedule (schedule_id, course_id, semester, start_time, end_time, meeting_days, room_number, academic_year, max_enrollment, current_enrollment) VALUES
('SCH101', 'CRS001', 'Fall', '09:00:00', '10:15:00', 'MWF', 'CS-101', 2025, 30, 0),
('SCH102', 'CRS002', 'Fall', '11:00:00', '12:15:00', 'TR', 'CS-102', 2025, 25, 0),
('SCH103', 'CRS003', 'Fall', '13:00:00', '14:15:00', 'MWF', 'MA-201', 2025, 35, 0),
('SCH104', 'CRS004', 'Fall', '14:30:00', '15:45:00', 'TR', 'PH-101', 2025, 30, 0),
('SCH105', 'CRS005', 'Fall', '10:30:00', '11:45:00', 'MWF', 'CH-101', 2025, 30, 0);

-- Test data for enrolled table
INSERT INTO enrolled (enrollment_id, student_id, schedule_id, enrollment_date, grade, status) VALUES
('ENR001', 'ST001', 'SCH101', '2025-08-25', NULL, 'enrolled'),
('ENR002', 'ST001', 'SCH102', '2025-08-25', NULL, 'enrolled'),
('ENR003', 'ST002', 'SCH103', '2025-08-26', NULL, 'enrolled'),
('ENR004', 'ST003', 'SCH104', '2025-08-26', NULL, 'enrolled'),
('ENR005', 'ST005', 'SCH101', '2025-08-27', NULL, 'enrolled');

-- Test data for teaching table
INSERT INTO teaching (teaching_id, professor_id, schedule_id) VALUES
('TCH001', 'PR001', 'SCH101'),
('TCH002', 'PR001', 'SCH102'),
('TCH003', 'PR002', 'SCH103'),
('TCH004', 'PR003', 'SCH104'),
('TCH005', 'PR004', 'SCH105');