-- Add level column to student table
ALTER TABLE student
ADD COLUMN level ENUM('undergraduate', 'graduate', 'phd') NOT NULL DEFAULT 'undergraduate';

-- Update existing students to have undergraduate level
UPDATE student SET level = 'undergraduate' WHERE level IS NULL; 