-- Test data for Student table
INSERT INTO Student (student_id, first_name, last_name, date_of_birth, major, status, enrollment_date, email) VALUES
(1, 'John', 'Smith', '2000-05-15', 'Computer Science', 'active', '2020-09-01', 'john.smith@university.edu'),
(2, 'Emma', 'Johnson', '2001-03-22', 'Mathematics', 'active', '2021-01-15', 'emma.j@university.edu'),
(3, 'Michael', 'Brown', '1999-11-30', 'Physics', 'active', '2019-09-01', 'michael.b@university.edu'),
(4, 'Sarah', 'Davis', '2000-07-18', 'Chemistry', 'graduated', '2019-09-01', 'sarah.d@university.edu'),
(5, 'David', 'Wilson', '2001-09-25', 'Computer Science', 'active', '2021-09-01', 'david.w@university.edu');

-- Test data for Professor table
INSERT INTO Professor (professor_id, first_name, last_name, department, hire_date, email) VALUES
(1, 'Robert', 'Anderson', 'Computer Science', '2015-08-15', 'r.anderson@university.edu'),
(2, 'Jennifer', 'Martinez', 'Mathematics', '2012-01-10', 'j.martinez@university.edu'),
(3, 'William', 'Taylor', 'Physics', '2010-09-01', 'w.taylor@university.edu'),
(4, 'Elizabeth', 'Thomas', 'Chemistry', '2018-06-20', 'e.thomas@university.edu');

-- Test data for Courses table
INSERT INTO Courses (course_id, course_code, course_name, description, credits, department) VALUES
(1, 'CS101', 'Introduction to Programming', 'Basic concepts of programming using Python', 3, 'Computer Science'),
(2, 'CS201', 'Data Structures', 'Advanced programming concepts and data structures', 4, 'Computer Science'),
(3, 'MATH201', 'Calculus I', 'Limits, derivatives, and basic integration', 4, 'Mathematics'),
(4, 'PHYS101', 'General Physics', 'Introduction to mechanics and thermodynamics', 4, 'Physics'),
(5, 'CHEM101', 'General Chemistry', 'Basic principles of chemistry', 4, 'Chemistry');

-- Test data for Prerequisite table
INSERT INTO Prerequisite (prerequisite_id, course_id, prerequisite_course_id) VALUES
(1, 2, 1), -- CS201 requires CS101
(2, 4, 3); -- PHYS101 requires MATH201

-- Test data for Schedule table
INSERT INTO Schedule (schedule_id, course_id, semester, start_time, end_time, meeting_days, room_num) VALUES
(1, 1, 'Fall 2023', '09:00:00', '10:15:00', 'MWF', 'CS-101'),
(2, 2, 'Fall 2023', '11:00:00', '12:15:00', 'TR', 'CS-102'),
(3, 3, 'Fall 2023', '13:00:00', '14:15:00', 'MWF', 'MA-201'),
(4, 4, 'Fall 2023', '14:30:00', '15:45:00', 'TR', 'PH-101'),
(5, 5, 'Fall 2023', '10:30:00', '11:45:00', 'MWF', 'CH-101');

-- Test data for Enrolled table
INSERT INTO Enrolled (enrollment_id, student_id, schedule_id, grade) VALUES
(1, 1, 1, 'A'),   -- John Smith in CS101
(2, 1, 2, 'B+'),  -- John Smith in CS201
(3, 2, 3, 'A-'),  -- Emma Johnson in MATH201
(4, 3, 4, 'B'),   -- Michael Brown in PHYS101
(5, 5, 1, NULL);  -- David Wilson in CS101 (grade not yet assigned)

-- Test data for Teaching table
INSERT INTO Teaching (teaching_id, professor_id, schedule_id) VALUES
(1, 1, 1), -- Prof. Anderson teaches CS101
(2, 1, 2), -- Prof. Anderson teaches CS201
(3, 2, 3), -- Prof. Martinez teaches MATH201
(4, 3, 4), -- Prof. Taylor teaches PHYS101
(5, 4, 5); -- Prof. Thomas teaches CHEM101