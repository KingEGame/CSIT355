from graphviz import Digraph

def create_er_diagram():
    # Create a new directed graph
    dot = Digraph(comment='University Course Management System ER Diagram')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Add entities
    dot.node('Student', '''Student
    student_id (PK)
    first_name
    last_name
    email
    date_of_birth
    major
    enrollment_date
    status''')
    
    dot.node('Professor', '''Professor
    professor_id (PK)
    first_name
    last_name
    email
    department
    hire_date
    status''')
    
    dot.node('Course', '''Course
    course_id (PK)
    course_code
    course_name
    description
    credits
    department
    level
    status''')
    
    dot.node('Schedule', '''Schedule
    schedule_id (PK)
    course_id (FK)
    semester
    academic_year
    meeting_days
    start_time
    end_time
    room_number
    building
    max_capacity''')
    
    dot.node('Teaching', '''Teaching
    teaching_id (PK)
    professor_id (FK)
    schedule_id (FK)''')
    
    dot.node('Enrollment', '''Enrollment
    enrollment_id (PK)
    student_id (FK)
    schedule_id (FK)
    enrollment_date
    grade
    status''')
    
    dot.node('Prerequisites', '''Prerequisites
    course_id (FK)
    prerequisite_id (FK)''')
    
    # Add relationships
    dot.edge('Student', 'Enrollment', 'enrolls in')
    dot.edge('Course', 'Schedule', 'has')
    dot.edge('Course', 'Prerequisites', 'has')
    dot.edge('Course', 'Prerequisites', 'is prerequisite for')
    dot.edge('Professor', 'Teaching', 'teaches')
    dot.edge('Schedule', 'Teaching', 'is taught in')
    dot.edge('Schedule', 'Enrollment', 'is enrolled in')
    
    # Save the diagram
    dot.render('er_diagram', format='png', cleanup=True)

if __name__ == '__main__':
    create_er_diagram() 