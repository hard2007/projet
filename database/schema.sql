PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('student', 'teacher')),
    full_name     TEXT NOT NULL,
    email         TEXT UNIQUE,
    group_name    TEXT,
    CHECK (role = 'student' OR group_name IS NULL OR group_name = '')
);

CREATE TABLE IF NOT EXISTS modules (
    module_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT NOT NULL UNIQUE,
    coefficient REAL NOT NULL CHECK (coefficient > 0),
    teacher_id  INTEGER NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS grades (
    grade_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER NOT NULL,
    module_id       INTEGER NOT NULL,
    exam_mark       REAL CHECK (exam_mark IS NULL OR exam_mark BETWEEN 0 AND 20),
    coursework_mark REAL CHECK (coursework_mark IS NULL OR coursework_mark BETWEEN 0 AND 20),
    UNIQUE (student_id, module_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_grades_student_id ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_grades_module_id ON grades(module_id);
CREATE INDEX IF NOT EXISTS idx_modules_teacher_id ON modules(teacher_id);
