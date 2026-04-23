-- =========================
-- FACULTY
-- =========================
INSERT INTO faculty (name, department, email) VALUES
('Dr. Mehta', 'Computer Science', 'mehta@univ.edu'),
('Prof. Sharma', 'Computer Science', 'sharma@univ.edu'),
('Dr. Patel', 'Electronics', 'patel@univ.edu'),
('Prof. Iyer', 'Physics', 'iyer@univ.edu'),
('Dr. Singh', 'Mathematics', 'singh@univ.edu');

-- =========================
-- COURSES
-- =========================
INSERT INTO course (name, code, lectures_per_week, is_lab, duration_hours) VALUES
('Mathematics', 'MTH101', 3, FALSE, 1.0),
('Physics', 'PHY101', 3, FALSE, 1.0),
('Chemistry', 'CHM101', 3, FALSE, 1.0),
('Data Structures', 'CSE201', 4, FALSE, 1.0),
('Operating Systems', 'CSE301', 4, FALSE, 1.0),
('DBMS Lab', 'CSE305L', 2, TRUE, 2.0),
('Physics Lab', 'PHY101L', 2, TRUE, 2.0);

-- =========================
-- BATCHES
-- =========================
INSERT INTO batch (name, size, semester) VALUES
('CSE-A', 60, 3),
('CSE-B', 55, 3),
('IT-A', 50, 3);

-- =========================
-- ROOMS
-- =========================
INSERT INTO room (name, room_number, building, capacity, is_lab) VALUES
('Room-101', 'Room-101', 'Main Block', 60, FALSE),
('Room-102', 'Room-102', 'Main Block', 50, FALSE),
('Room-103', 'Room-103', 'Science Block', 70, FALSE),
('Lab-1', 'Lab-1', 'CS Block', 40, TRUE),
('Lab-2', 'Lab-2', 'CS Block', 35, TRUE);

-- =========================
-- TIMESLOTS (Mon-Fri, 5 per day)
-- =========================
INSERT INTO timeslot (day, start_time, end_time) VALUES
('Monday', '09:00', '10:00'),
('Monday', '10:00', '11:00'),
('Monday', '11:00', '12:00'),
('Monday', '13:00', '14:00'),
('Monday', '14:00', '15:00'),

('Tuesday', '09:00', '10:00'),
('Tuesday', '10:00', '11:00'),
('Tuesday', '11:00', '12:00'),
('Tuesday', '13:00', '14:00'),
('Tuesday', '14:00', '15:00'),

('Wednesday', '09:00', '10:00'),
('Wednesday', '10:00', '11:00'),
('Wednesday', '11:00', '12:00'),
('Wednesday', '13:00', '14:00'),
('Wednesday', '14:00', '15:00'),

('Thursday', '09:00', '10:00'),
('Thursday', '10:00', '11:00'),
('Thursday', '11:00', '12:00'),
('Thursday', '13:00', '14:00'),
('Thursday', '14:00', '15:00'),

('Friday', '09:00', '10:00'),
('Friday', '10:00', '11:00'),
('Friday', '11:00', '12:00'),
('Friday', '13:00', '14:00'),
('Friday', '14:00', '15:00');

-- =========================
-- FACULTY AVAILABILITY (sample mapping)
-- =========================
INSERT INTO faculty_availability (faculty_id, timeslot_id)
SELECT f.id, t.id
FROM faculty f, timeslot t
WHERE t.id % 2 = f.id % 2;  -- simple distribution for demo

-- =========================
-- CONSTRAINT RULES (optional)
-- =========================
INSERT INTO constraint_rules (name, value) VALUES
('max_lectures_per_day', '3'),
('no_back_to_back', 'true'),
('lab_priority', 'true');