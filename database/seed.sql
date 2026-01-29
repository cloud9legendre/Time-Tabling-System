-- 1. Departments
INSERT INTO departments (code, name, is_active) VALUES 
('CSE', 'Computer Science & Engineering', true),
('ENTC', 'Electronic & Telecommunication', true),
('MATH', 'Mathematics', true),
('MECH', 'Mechanical Engineering', true)
ON CONFLICT (code) DO NOTHING;

-- 2. Labs (Includes is_active)
INSERT INTO labs (name, department_code, capacity, is_active) VALUES 
('High Performance Computing Lab', 'CSE', 60, true),
('Hardware Lab', 'CSE', 30, true),
('Analog Electronics Lab', 'ENTC', 45, true),
('Robotics Lab', 'ENTC', 25, true),
('Fluid Mechanics Lab', 'MECH', 20, true)
ON CONFLICT DO NOTHING;

-- 3. Instructors 
-- Passwords are hashed. Hash for 'password123': $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
-- Includes Profile Fields: University, Degree, Graduated Date
INSERT INTO instructors (email, name, department_code, role, password, university, degree, graduated_date, is_active) VALUES 
('perera@uom.lk', 'Prof. Perera', 'CSE', 'ADMIN', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'UoM', 'PhD in AI', '1995-05-20', true),
('silva@uom.lk', 'Dr. Silva', 'ENTC', 'INSTRUCTOR', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'NUS', 'MSc Electronics', '2010-08-15', true),
('fernando@uom.lk', 'Dr. Fernando', 'MATH', 'INSTRUCTOR', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'Colombo', 'PhD Mathematics', '2005-01-10', true),
('admin@uom.lk', 'System Admin', 'CSE', 'SUPER_ADMIN', '$2a$12$iLS26XR22/l/gSO0iPzrvew3KHVpMJNIaDud4R0B8rri29Ssb/D7W', 'UoM', 'BSc Eng', '2020-01-01', true)
ON CONFLICT (email) DO NOTHING;

-- 4. Modules (Includes Semester)
INSERT INTO modules (code, title, offering_dept, enrolled_count, semester, is_active) VALUES 
('CS1032', 'Programming Fundamentals', 'CSE', 200, 1, true),
('MA1013', 'Calculus I', 'MATH', 200, 1, true),
('EN2012', 'Analog Circuits', 'ENTC', 100, 3, true),
('CS2022', 'Data Structures & Algorithms', 'CSE', 150, 3, true),
('CS3042', 'Database Systems', 'CSE', 140, 5, true),
('ME2050', 'Thermodynamics', 'MECH', 80, 4, true),
('CS4200', 'High Performance Computing', 'CSE', 60, 7, true)
ON CONFLICT (code) DO NOTHING;