-- Migration 001: privacy by design (decisions P1, P2, P6 of the report, section 5.2.7)
-- Run once on hotel_system_db, e.g. in MySQL Workbench.
USE hotel_system_db;

-- P1: stop collecting the national ID (not needed by FR1 to FR9)
ALTER TABLE Guest DROP COLUMN SSN;

-- P2: record when the guest accepted the privacy notice
ALTER TABLE Guest ADD COLUMN Privacy_Consent_At DATETIME NULL;

-- P6: mark accounts that were anonymized on request
ALTER TABLE Guest ADD COLUMN Is_Anonymized TINYINT(1) NOT NULL DEFAULT 0;

-- P6 example, NOT part of the migration. It is run by the application
-- when a guest asks to delete the account (the application passes the guest id):
--   UPDATE Guest
--   SET Name = 'Deleted user',
--       Email = CONCAT('deleted_', Guest_ID, '@invalid.local'),
--       Phone = '', Password_Hash = '', Is_Anonymized = 1
--   WHERE Guest_ID = ?;
