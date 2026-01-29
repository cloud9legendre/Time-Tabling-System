-- Phase 4: PostgreSQL Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

CREATE TABLE departments (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE labs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_code VARCHAR(10) REFERENCES departments(code),
    capacity INT NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE instructors (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_code VARCHAR(10) REFERENCES departments(code),
    role VARCHAR(20) DEFAULT 'INSTRUCTOR',
    password VARCHAR(100) DEFAULT 'password123', -- Phase 7 Addition
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE modules (
    code VARCHAR(15) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    offering_dept VARCHAR(10) REFERENCES departments(code),
    enrolled_count INT DEFAULT 0
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lab_id INT NOT NULL REFERENCES labs(id),
    module_code VARCHAR(15) REFERENCES modules(code),
    booked_by_id INT NOT NULL REFERENCES instructors(id),
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    purpose VARCHAR(20) DEFAULT 'CLASS',
    
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    CONSTRAINT no_overlap EXCLUDE USING GIST (
        lab_id WITH =,
        booking_date WITH =,
        tsrange(booking_date + start_time, booking_date + end_time) WITH &&
    ) WHERE (status NOT IN ('CANCELLED', 'REJECTED'))
);
