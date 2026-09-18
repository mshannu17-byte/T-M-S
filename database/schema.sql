-- =========================================================
-- CARELINE TELEMEDICINE SYSTEM
-- MySQL Database
-- =========================================================

CREATE DATABASE IF NOT EXISTS careline_db;

USE careline_db;

-- =========================================================
-- USERS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL,
    status ENUM('active', 'pending', 'rejected', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- PATIENTS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    date_of_birth DATE,
    gender VARCHAR(20),
    address VARCHAR(255),
    blood_group VARCHAR(10),
    emergency_contact VARCHAR(20),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================================================
-- DOCTORS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(150),
    experience INT DEFAULT 0,
    license_number VARCHAR(100),
    consultation_fee DECIMAL(10,2) DEFAULT 0.00,
    about TEXT,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================================================
-- APPOINTMENTS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,

    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,

    reason TEXT,

    status ENUM(
        'pending',
        'accepted',
        'rejected',
        'completed',
        'cancelled'
    ) DEFAULT 'pending',

    meeting_link VARCHAR(500),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE CASCADE
);

-- =========================================================
-- CONSULTATIONS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS consultations (
    id INT AUTO_INCREMENT PRIMARY KEY,

    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,

    symptoms TEXT,
    diagnosis TEXT,
    prescription TEXT,
    doctor_notes TEXT,

    consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (appointment_id)
        REFERENCES appointments(id)
        ON DELETE CASCADE,

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE CASCADE
);

-- =========================================================
-- MEDICAL RECORDS TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,

    patient_id INT NOT NULL,
    doctor_id INT,

    record_type VARCHAR(100),
    title VARCHAR(200),
    description TEXT,
    file_path VARCHAR(500),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE SET NULL
);

-- =========================================================
-- PASSWORD RESET TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS password_resets (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,
    reset_token VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================================================
-- AI CHAT HISTORY TABLE
-- =========================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,

    patient_id INT NOT NULL,

    sender ENUM('patient', 'ai') NOT NULL,
    message TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);

-- =========================================================
-- DEFAULT ADMIN ACCOUNT
-- =========================================================

INSERT INTO users
(
    full_name,
    email,
    phone,
    password,
    role,
    status
)
SELECT
    'CareLine Administrator',
    'admin@careline.com',
    '9999999999',
    'scrypt:32768:8:1$4Ir4OrkAWGm72B3R$9c1db0478afa518925f320deb102dc09cfeba71981c04a86441ac11154bc5b2bccde169328268b3e963223b072ad99a151f17a596c5d0aab8ce51b0f9646b3ce',
    'admin',
    'active'
WHERE NOT EXISTS
(
    SELECT 1
    FROM users
    WHERE email = 'admin@careline.com'
);

-- =========================================================
-- DATABASE COMPLETE
-- =========================================================