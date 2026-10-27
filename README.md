# SmartGrades — Python, Tkinter and SQLite

SmartGrades is a desktop prototype for managing university student accounts, modules,
groups, and grades. It uses **exactly three application tables**: `users`, `modules`,
and `grades`.

## Features included

- Login with separate student and teacher dashboards.
- Password hashing using PBKDF2-HMAC-SHA256.
- Student dashboard: group, module list, coursework/exam marks, module averages,
  and weighted semester average.
- Teacher dashboard: view assigned modules, enter/update grades for assigned modules,
  view student roster, and assign student groups.
- SQLite foreign keys, mark validation, and parameterized SQL queries.
- One teacher can be assigned to multiple modules.
- No third-party packages are required.

## Requirements

- Python 3.10+ recommended.
- Tkinter available in your Python installation.
- SQLite is accessed via Python's built-in `sqlite3` module.

## Start the application

Run these commands from the project folder:

```bash
python main.py
```

This initializes `database/students.db` if necessary, then opens the login screen.

## Create demonstration data

Run this from the project folder to create or refresh the local demonstration data:

```bash
python create_demo_users.py
```

The seed includes 60 fictional students in groups G1-G4, five teachers, six modules,
and sample coursework and exam marks for each student. All teacher accounts use
`TeacherDemo123!`; all student accounts use `StudentDemo123!`. The complete account
list is in [DEMO_CREDENTIALS.txt](./DEMO_CREDENTIALS.txt). Running the seed again
resets passwords for these demo usernames and fills in any missing sample data.

These are public demo credentials for local testing only. Do not use this file or these
accounts for real student information, and do not commit real student data or passwords
to GitHub.

## Database structure

- `users`: login account, role, identity, and student group.
- `modules`: module name, coefficient, and responsible teacher (`teacher_id`).
- `grades`: coursework and exam marks per student and module.

The database is created by `database.py` using `database/schema.sql`. `students.db` is
runtime data and is intentionally ignored by Git.

## Mark calculation

- Coursework weight: 40%
- Exam weight: 60%
- Module average = coursework × 0.40 + exam × 0.60
- Semester average = sum(module average × coefficient) / sum(coefficients for modules
  with both marks entered)

You can change the weights in `services/grade_service.py` to match your professor's rules.

## Project structure

```text
SmartGrades/
├── main.py
├── database.py
├── create_demo_users.py
├── database/
│   └── schema.sql
├── models/
│   ├── user.py
│   ├── module.py
│   └── grade.py
├── repositories/
│   ├── user_repository.py
│   ├── module_repository.py
│   └── grade_repository.py
├── services/
│   ├── auth_service.py
│   ├── module_service.py
│   └── grade_service.py
├── ui/
│   └── main_window.py
└── tests/
    └── test_schema.py
```

## GitHub

```bash
git init
git add .
git commit -m "Initial SmartGrades application"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

## Important scope notes

This is a student-project prototype, not a production authentication system. The app
currently supports teacher grade entry for assigned modules and student group assignment.
Module creation is provided by the service layer and demo setup, but a full module-creation
form, account-management screen, password-reset workflow, and production-grade audit trail
are not included yet. The three-table limit means groups are stored as text on student
accounts instead of a separate groups table.
