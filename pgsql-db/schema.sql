-- =========================
-- RESET DATABASE (SAFE RE-RUN)
-- =========================
DROP TABLE IF EXISTS timetable CASCADE;
DROP TABLE IF EXISTS conflicts CASCADE;
DROP TABLE IF EXISTS constraint_rules CASCADE;
DROP TABLE IF EXISTS faculty_availability CASCADE;
DROP TABLE IF EXISTS faculty CASCADE;
DROP TABLE IF EXISTS course CASCADE;
DROP TABLE IF EXISTS batch CASCADE;
DROP TABLE IF EXISTS room CASCADE;
DROP TABLE IF EXISTS timeslot CASCADE;

-- =========================
-- FACULTY
-- =========================
CREATE TABLE faculty (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    email VARCHAR(120)
);

-- =========================
-- COURSE
-- =========================
CREATE TABLE course (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50),
    lectures_per_week INT NOT NULL CHECK (lectures_per_week > 0),
    is_lab BOOLEAN DEFAULT FALSE,
    duration_hours NUMERIC(4,2) DEFAULT 1.0
);

-- =========================
-- BATCH
-- =========================
CREATE TABLE batch (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    size INT NOT NULL CHECK (size > 0),
    semester INT DEFAULT 1
);

-- =========================
-- ROOM
-- =========================
CREATE TABLE room (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    room_number VARCHAR(50),
    building VARCHAR(100),
    capacity INT NOT NULL CHECK (capacity > 0),
    is_lab BOOLEAN DEFAULT FALSE
);

-- =========================
-- TIMESLOT
-- =========================
CREATE TABLE timeslot (
    id SERIAL PRIMARY KEY,
    day VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    CHECK (start_time < end_time)
);

-- =========================
-- FACULTY AVAILABILITY
-- =========================
CREATE TABLE faculty_availability (
    id SERIAL PRIMARY KEY,
    faculty_id INT REFERENCES faculty(id) ON DELETE CASCADE,
    timeslot_id INT REFERENCES timeslot(id) ON DELETE CASCADE,
    UNIQUE (faculty_id, timeslot_id)
);

-- =========================
-- CONSTRAINT RULES
-- =========================
CREATE TABLE constraint_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value TEXT
);

-- =========================
-- TIMETABLE
-- =========================
CREATE TABLE timetable (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES course(id) ON DELETE CASCADE,
    faculty_id INT REFERENCES faculty(id) ON DELETE CASCADE,
    batch_id INT REFERENCES batch(id) ON DELETE CASCADE,
    room_id INT REFERENCES room(id) ON DELETE CASCADE,
    timeslot_id INT REFERENCES timeslot(id) ON DELETE CASCADE,
    UNIQUE (batch_id, timeslot_id),
    UNIQUE (faculty_id, timeslot_id),
    UNIQUE (room_id, timeslot_id)
);

-- =========================
-- CONFLICTS
-- =========================
CREATE TABLE conflicts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- INDEXES (PERFORMANCE)
-- =========================
CREATE INDEX idx_timetable_batch ON timetable(batch_id);
CREATE INDEX idx_timetable_faculty ON timetable(faculty_id);
CREATE INDEX idx_timetable_room ON timetable(room_id);