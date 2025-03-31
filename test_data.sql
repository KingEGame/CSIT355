-- Insert sample students
INSERT INTO Student (student_id, first_name, last_name, email, date_of_birth, major, enrollment_date, status) VALUES
                                                                                                                  ('S001', 'John', 'Doe', 'john.doe@university.edu', '2000-01-15', 'Computer Science', '2023-09-01', 'active'),
                                                                                                                  ('S002', 'Jane', 'Smith', 'jane.smith@university.edu', '2000-03-22', 'Computer Science', '2023-09-01', 'active'),
                                                                                                                  ('S003', 'Michael', 'Johnson', 'michael.j@university.edu', '1999-07-10', 'Mathematics', '2023-09-01', 'active'),
                                                                                                                  ('S004', 'Sarah', 'Williams', 'sarah.w@university.edu', '2000-11-05', 'Physics', '2023-09-01', 'active'),
                                                                                                                  ('S005', 'David', 'Brown', 'david.b@university.edu', '2001-02-28', 'Computer Science', '2023-09-01', 'active'),
                                                                                                                  ('S006', 'Emily', 'Davis', 'emily.d@university.edu', '2000-09-12', 'Mathematics', '2023-09-01', 'active'),
                                                                                                                  ('S007', 'Robert', 'Wilson', 'robert.w@university.edu', '1999-12-25', 'Physics', '2023-09-01', 'active'),
                                                                                                                  ('S008', 'Lisa', 'Anderson', 'lisa.a@university.edu', '2000-04-18', 'Computer Science', '2023-09-01', 'active'),
                                                                                                                  ('S009', 'James', 'Taylor', 'james.t@university.edu', '2001-06-30', 'Mathematics', '2023-09-01', 'active'),
                                                                                                                  ('S010', 'Jennifer', 'Martinez', 'jennifer.m@university.edu', '2000-08-14', 'Physics', '2023-09-01', 'active');

-- Insert sample professors
INSERT INTO Professor (professor_id, first_name, last_name, email, department, hire_date, status) VALUES
                                                                                                      ('P001', 'Alice', 'Johnson', 'alice.j@university.edu', 'Computer Science', '2020-01-15', 'active'),
                                                                                                      ('P002', 'Robert', 'Smith', 'robert.s@university.edu', 'Mathematics', '2019-06-20', 'active'),
                                                                                                      ('P003', 'Mary', 'Williams', 'mary.w@university.edu', 'Physics', '2018-08-30', 'active'),
                                                                                                      ('P004', 'David', 'Brown', 'david.brown@university.edu', 'Computer Science', '2017-09-01', 'active'),
                                                                                                      ('P005', 'Sarah', 'Davis', 'sarah.d@university.edu', 'Mathematics', '2021-01-10', 'active'),
                                                                                                      ('P006', 'Michael', 'Wilson', 'michael.w@university.edu', 'Physics', '2019-12-15', 'active'),
                                                                                                      ('P007', 'Emma', 'Anderson', 'emma.a@university.edu', 'Computer Science', '2020-07-01', 'active'),
                                                                                                      ('P008', 'James', 'Taylor', 'james.taylor@university.edu', 'Mathematics', '2018-03-20', 'active'),
                                                                                                      ('P009', 'Sophia', 'Martinez', 'sophia.m@university.edu', 'Physics', '2022-01-05', 'active'),
                                                                                                      ('P010', 'William', 'Lee', 'william.l@university.edu', 'Computer Science', '2021-08-15', 'active');

-- Insert sample courses
INSERT INTO Course (course_id, course_code, course_name, description, credits, department, level) VALUES
                                                                                                      ('CSE102', 'CSE102', 'Data Structures', 'Fundamental data structures and algorithms', 3, 'Computer Science', 'undergraduate'),
                                                                                                      ('CSE201', 'CSE201', 'Database Systems', 'Design and implementation of database systems', 3, 'Computer Science', 'undergraduate'),
                                                                                                      ('CSE202', 'CSE202', 'Web Development', 'Modern web development technologies and frameworks', 3, 'Computer Science', 'undergraduate'),
                                                                                                      ('MTH101', 'MTH101', 'Calculus I', 'Introduction to differential and integral calculus', 4, 'Mathematics', 'undergraduate'),
                                                                                                      ('MTH102', 'MTH102', 'Linear Algebra', 'Study of linear equations and vector spaces', 3, 'Mathematics', 'undergraduate'),
                                                                                                      ('PHY101', 'PHY101', 'Classical Mechanics', 'Basic principles of classical mechanics', 4, 'Physics', 'undergraduate'),
                                                                                                      ('PHY102', 'PHY102', 'Electromagnetism', 'Study of electric and magnetic fields', 4, 'Physics', 'undergraduate'),
                                                                                                      ('CSE301', 'CSE301', 'Software Engineering', 'Software development methodologies and practices', 3, 'Computer Science', 'undergraduate'),
                                                                                                      ('CSE302', 'CSE302', 'Computer Networks', 'Network protocols and architecture', 3, 'Computer Science', 'undergraduate');

-- Insert course prerequisites
INSERT INTO Prerequisites (course_id, prerequisite_id) VALUES
                                                           ('CSE102', 'CSE101'),
                                                           ('CSE201', 'CSE102'),
                                                           ('CSE202', 'CSE101'),
                                                           ('MTH102', 'MTH101'),
                                                           ('PHY102', 'PHY101'),
                                                           ('CSE301', 'CSE201'),
                                                           ('CSE302', 'CSE201');

-- Insert sample schedules
INSERT INTO Schedule (schedule_id, course_id, semester, academic_year, meeting_days, start_time, end_time, room_number, building) VALUES
                                                                                                                                      ('SCH001', 'CSE101', 'Fall', 2024, 'MWF', '09:00:00', '10:30:00', '101', 'Computer Science Building'),
                                                                                                                                      ('SCH002', 'CSE232', 'Fall', 2024, 'TR', '14:00:00', '15:30:00', '102', 'Computer Science Building'),
                                                                                                                                      ('SCH003', 'CSE331', 'Fall', 2024, 'MWF', '11:00:00', '12:30:00', '201', 'Computer Science Building'),
                                                                                                                                      ('SCH004', 'CSE435', 'Fall', 2024, 'TR', '09:00:00', '10:30:00', '301', 'Computer Science Building'),
                                                                                                                                      ('SCH005', 'CSE480', 'Fall', 2024, 'MWF', '14:00:00', '15:30:00', '401', 'Computer Science Building');

-- Insert teaching assignments
INSERT INTO Teaching (teaching_id, professor_id, schedule_id) VALUES
                                                                  ('T001', 'P001', 'SCH001'),
                                                                  ('T002', 'P004', 'SCH002'),
                                                                  ('T003', 'P007', 'SCH003'),
                                                                  ('T004', 'P010', 'SCH004'),
                                                                  ('T005', 'P001', 'SCH005');

-- Insert prerequisites
INSERT INTO Prerequisites (course_id, prerequisite_id) VALUES
                                                           ('CSE232', 'CSE101'),
                                                           ('CSE331', 'CSE232'),
                                                           ('CSE435', 'CSE331'),
                                                           ('CSE480', 'CSE331');

-- Insert sample enrollments
INSERT INTO Enrollment (enrollment_id, student_id, schedule_id, enrollment_date, status) VALUES
                                                                                             ('E001', 'S001', 'SCH001', '2024-08-15', 'enrolled'),
                                                                                             ('E002', 'S002', 'SCH001', '2024-08-15', 'enrolled'),
                                                                                             ('E003', 'S003', 'SCH002', '2024-08-15', 'enrolled'),
                                                                                             ('E004', 'S004', 'SCH002', '2024-08-15', 'enrolled'),
                                                                                             ('E005', 'S005', 'SCH003', '2024-08-15', 'enrolled'),
                                                                                             ('E006', 'S006', 'SCH003', '2024-08-15', 'enrolled'),
                                                                                             ('E007', 'S007', 'SCH004', '2024-08-15', 'enrolled'),
                                                                                             ('E008', 'S008', 'SCH004', '2024-08-15', 'enrolled'),
                                                                                             ('E009', 'S009', 'SCH005', '2024-08-15', 'enrolled'),
                                                                                             ('E010', 'S010', 'SCH005', '2024-08-15', 'enrolled');
