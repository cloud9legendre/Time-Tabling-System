-- 1. Departments
INSERT INTO departments (code, name, is_active) VALUES 
('CSE', 'Computer Science & Engineering', true),
('ENTC', 'Electronic & Telecommunication', true),
('MATH', 'Mathematics', true),
('MECH', 'Mechanical Engineering', true)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, is_active = EXCLUDED.is_active;

-- 2. Labs (Explicit IDs for referencing)
INSERT INTO labs (id, name, department_code, capacity, is_active) VALUES 
(1, 'High Performance Computing Lab', 'CSE', 60, true),
(2, 'Hardware Lab', 'CSE', 30, true),
(3, 'Analog Electronics Lab', 'ENTC', 45, true),
(4, 'Robotics Lab', 'ENTC', 25, true),
(5, 'Fluid Mechanics Lab', 'MECH', 20, true)
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name, 
    department_code = EXCLUDED.department_code, 
    capacity = EXCLUDED.capacity, 
    is_active = EXCLUDED.is_active;

-- Reset sequence to avoid id 1-5 collisions if manual inserts occur later
SELECT setval('labs_id_seq', (SELECT MAX(id) FROM labs));

-- 3. Instructors 
-- Passwords are hashed. Hash for 'password123': $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
INSERT INTO instructors (id, email, name, department_code, role, password, university, degree, graduated_date, is_active, photo_url) VALUES 
(1, 'perera@uom.lk', 'Prof. Perera', 'CSE', 'ADMIN', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'UoM', 'PhD in AI', '1995-05-20', true, NULL),
(2, 'silva@uom.lk', 'Dr. Silva', 'ENTC', 'INSTRUCTOR', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'NUS', 'MSc Electronics', '2010-08-15', true, NULL),
(3, 'fernando@uom.lk', 'Dr. Fernando', 'MATH', 'INSTRUCTOR', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'Colombo', 'PhD Mathematics', '2005-01-10', true, NULL),
(4, 'admin@uom.lk', 'System Admin', 'CSE', 'SUPER_ADMIN', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'UoM', 'BSc Eng', '2020-01-01', true, NULL)
ON CONFLICT (email) DO UPDATE SET 
    name = EXCLUDED.name, 
    department_code = EXCLUDED.department_code, 
    role = EXCLUDED.role,
    password = EXCLUDED.password,
    university = EXCLUDED.university,
    degree = EXCLUDED.degree,
    graduated_date = EXCLUDED.graduated_date,
    is_active = EXCLUDED.is_active,
    photo_url = EXCLUDED.photo_url;

-- Reset sequence for instructors
SELECT setval('instructors_id_seq', (SELECT MAX(id) FROM instructors));

-- 4. Modules
INSERT INTO modules (code, title, offering_dept, enrolled_count, semester, is_active) VALUES 
('CS1032', 'Programming Fundamentals', 'CSE', 200, 1, true),
('MA1013', 'Calculus I', 'MATH', 200, 1, true),
('EN2012', 'Analog Circuits', 'ENTC', 100, 3, true),
('CS2022', 'Data Structures & Algorithms', 'CSE', 150, 3, true),
('CS3042', 'Database Systems', 'CSE', 140, 5, true),
('ME2050', 'Thermodynamics', 'MECH', 80, 4, true),
('CS4200', 'High Performance Computing', 'CSE', 60, 7, true)
ON CONFLICT (code) DO UPDATE SET 
    title = EXCLUDED.title, 
    offering_dept = EXCLUDED.offering_dept, 
    enrolled_count = EXCLUDED.enrolled_count, 
    semester = EXCLUDED.semester, 
    is_active = EXCLUDED.is_active;

-- 5. Leaves (New)
INSERT INTO leaves (instructor_id, start_date, end_date, reason, status) VALUES 
(2, '2024-03-10', '2024-03-12', 'Medical Leave', 'APPROVED'),
(2, '2024-04-05', '2024-04-06', 'Personal', 'PENDING'),
(3, '2024-03-20', '2024-03-22', 'Conference', 'REJECTED')
ON CONFLICT DO NOTHING;

-- 6. Bookings (New) - IDs used from explicit inserts above
-- Using hardcoded UUIDs for consistency in seed
INSERT INTO bookings (id, lab_id, module_code, booked_by_id, booking_date, start_time, end_time, status, purpose, practical_name) VALUES 
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 1, 'CS4200', 1, CURRENT_DATE + INTERVAL '1 day', '08:00:00', '10:00:00', 'CONFIRMED', 'CLASS', 'HPC Basics'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 1, 'CS4200', 1, CURRENT_DATE + INTERVAL '2 days', '10:00:00', '12:00:00', 'CONFIRMED', 'CLASS', 'MPI Programming'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 2, 'CS1032', 4, CURRENT_DATE + INTERVAL '1 day', '13:00:00', '15:00:00', 'PENDING', 'EXAM', 'Mid-Semester Exam'),
('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 3, 'EN2012', 2, CURRENT_DATE - INTERVAL '2 days', '09:00:00', '11:00:00', 'CONFIRMED', 'CLASS', 'Op-Amps Practical')
ON CONFLICT (id) DO NOTHING;