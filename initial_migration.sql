-- Database Schema for Biometric Attendance System
-- Compatible with both PostgreSQL and SQLite

-- Enable UUID extension (PostgreSQL only)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Students Table
CREATE TABLE students (
                          student_id VARCHAR(50) PRIMARY KEY,      -- External system's student ID
                          enrollment_code VARCHAR(50) UNIQUE,       -- University enrollment code
                          first_name VARCHAR(100) NOT NULL,
                          last_name VARCHAR(100) NOT NULL,
                          face_encoding TEXT,                      -- Stored face encoding data (base64)
                          face_encoding_updated_at TIMESTAMP,      -- Last update of face encoding
                          is_active BOOLEAN DEFAULT true,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance Records Table
CREATE TABLE attendance_records (
                                    attendance_id SERIAL PRIMARY KEY,        -- Auto-incrementing ID
                                    student_id VARCHAR(50) NOT NULL,
                                    capture_timestamp TIMESTAMP NOT NULL,     -- When the attendance was captured
                                    confidence_score FLOAT,                   -- Face recognition confidence score
                                    device_id VARCHAR(50) NOT NULL,           -- ID of the device that captured attendance
                                    sync_status VARCHAR(20) DEFAULT 'pending' -- pending, synced, failed
                                        CHECK (sync_status IN ('pending', 'synced', 'failed')),
                                    sync_timestamp TIMESTAMP,                 -- When the record was synced
                                    sync_attempts INTEGER DEFAULT 0,          -- Number of sync attempts
                                    last_sync_error TEXT,                    -- Last error message if sync failed
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Sync Log Table (for tracking synchronization history)
CREATE TABLE sync_logs (
                           log_id SERIAL PRIMARY KEY,
                           sync_start_timestamp TIMESTAMP NOT NULL,
                           sync_end_timestamp TIMESTAMP,
                           records_processed INTEGER DEFAULT 0,
                           records_succeeded INTEGER DEFAULT 0,
                           records_failed INTEGER DEFAULT 0,
                           sync_status VARCHAR(20) DEFAULT 'in_progress'
                               CHECK (sync_status IN ('in_progress', 'completed', 'failed')),
                           error_message TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices Table (for managing multiple capture devices)
CREATE TABLE devices (
                         device_id VARCHAR(50) PRIMARY KEY,
                         device_name VARCHAR(100) NOT NULL,
                         location VARCHAR(100),
                         last_sync_timestamp TIMESTAMP,
                         is_active BOOLEAN DEFAULT true,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_attendance_student_id ON attendance_records(student_id);
CREATE INDEX idx_attendance_capture_timestamp ON attendance_records(capture_timestamp);
CREATE INDEX idx_attendance_sync_status ON attendance_records(sync_status);
CREATE INDEX idx_students_enrollment ON students(enrollment_code);

-- Create a view for pending synchronizations
CREATE VIEW pending_attendance_sync AS
SELECT
    ar.attendance_id,
    ar.student_id,
    s.enrollment_code,
    ar.capture_timestamp,
    ar.device_id,
    ar.sync_attempts
FROM attendance_records ar
         JOIN students s ON ar.student_id = s.student_id
WHERE ar.sync_status = 'pending'
ORDER BY ar.capture_timestamp;