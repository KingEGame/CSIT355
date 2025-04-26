# Course Management System

## Project Description

The Course Management System is a comprehensive web-based application designed to streamline and automate the academic course management process at universities. It provides a centralized platform for students, professors, and administrative staff to manage courses, enrollments, academic progress, and more.

---

## Project Structure

```
Project/
├── web/
│   ├── __init__.py                # App factory, blueprint registration
│   ├── app.py                     # Entrypoint for running the Flask app
│   ├── config.py                  # Configuration (env, DB, session, upload)
│   ├── models.py                  # SQLAlchemy models and enums
│   ├── forms.py                   # WTForms for user input and validation
│   ├── blueprints/                # Modular blueprints (admin, students, professors)
│   │   ├── admin.py
│   │   ├── students.py
│   │   └── professors.py
│   ├── routes/                    # Additional route modules (auth, course, etc.)
│   │   ├── auth_routes.py
│   │   ├── student_routes.py
│   │   ├── professor_routes.py
│   │   ├── course_routes.py
│   │   └── admin_routes.py
│   ├── templates/                 # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── student/
│   │   ├── professor/
│   │   ├── admin/
│   │   └── shared/
│   ├── static/                    # Static assets (CSS, JS)
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── main.js
│   │       └── script.js
│   └── uploads/                   # File uploads (if used)
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker setup for MySQL
├── test_db.py                     # DB connection test script
├── .env.example                   # Example environment variables
├── .gitignore
└── README.md
```

---

## Key Features & Workflows

### Modular Flask App
- App factory pattern (`create_app`) for flexible configuration and testing.
- Blueprints for `students`, `professors`, `admin`, and `auth` keep routes organized and maintainable.

### Authentication & Authorization
- Session-based login for students, professors, and admin.
- Role-based access enforced via session checks and decorators.
- Registration routes for both students and professors.

### User Dashboards
- **Students**: Dashboard with credit progress, GPA, current courses, academic history, and profile management.
- **Professors**: Dashboard with teaching load, course management, and profile management.
- **Admins**: Dashboard with statistics, user/course management, and analytics.

### Course & Enrollment Management
- Courses have levels (undergraduate, graduate, PhD), prerequisites, and capacity constraints.
- Students enroll in courses via schedules; enrollments track grades and status.
- Professors are assigned to schedules (teaching assignments).

### Forms & Validation
- WTForms for all user input (registration, profile, course creation, etc.).
- Custom validation for emails, course codes, prerequisites, and password changes.

### Database Design (Detailed)
- **Student**: Tracks status, level, major, enrollments, and email (with constraints).
- **Professor**: Tracks department, contact info, teaching assignments.
- **Course**: Has code, name, description, credits, department, level, prerequisites.
- **Schedule**: Links courses to semesters, times, rooms, and professors.
- **Enrolled**: Tracks student enrollments, grades, and status.
- **Teaching**: Links professors to schedules.
- **Enums**: For student/professor status, course level, semester, grade, enrollment status.
- **Constraints**: Email format, course credit/capacity, no self-prerequisite, minimum student age.

### Admin Features
- Add/edit/delete students, professors, and courses.
- Assign/remove teaching assignments.
- View dashboards with statistics and analytics.
- Filter/search users and courses.

### Frontend
- Responsive design using custom CSS and JS.
- Jinja2 templates for dynamic content.
- Separate template folders for each user type.

### Configuration & Environment
- Uses `.env` for secrets and DB config.
- `config.py` supports development, production, and testing configs.
- File upload folder is auto-created if needed.

### Docker & Database
- `docker-compose.yml` sets up a MySQL 8.0 container with persistent storage.
- MySQL credentials and DB name are set via environment variables.
- Database schema and test data are initialized via scripts.

### Testing & Utilities
- `test_db.py` script to verify DB connectivity and query execution.

---

## Deployment

### Local Deployment

1. **Clone the Repository**
2. **Set Up Virtual Environment**
3. **Install Dependencies**
4. **Configure `.env`**
5. **Start MySQL with Docker**
   ```bash
   docker-compose up -d
   ```
6. **Initialize Database**
   ```bash
   python main.py --init-db
   python main.py --load-test-data  # Optional
   ```
7. **Run the Application**
   ```bash
   python main.py
   ```
8. **Access at** `http://localhost:5000`

### Dockerized Database

- The app expects MySQL to be running at `127.0.0.1:3306` with credentials as in `docker-compose.yml`.
- Data is persisted in a Docker volume.

### Environment Variables

- `SECRET_KEY`: Flask secret key
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: MySQL connection info

---

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Session
- SQLAlchemy
- PyMySQL
- python-dotenv
- Werkzeug
- cryptography
- email-validator

---

## Development & Testing

- Use `test_db.py` to verify DB connection.
- Modular blueprints and app factory make it easy to add features and test components.
- All forms and models have built-in validation.

---

## Support

For additional help:
1. Check the comments in the code
2. Review the SQL schema in `schema.sql`
3. Examine the test data in `test_data.sql`
4. Contact the development team

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is used for educational purposes at Montclair State University. 