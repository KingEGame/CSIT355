-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS csit555;

-- Use the database
USE csit555;

-- Create a user if it doesn't exist and grant privileges
CREATE USER IF NOT EXISTS 'db'@'%' IDENTIFIED BY 'csit_555';
GRANT ALL PRIVILEGES ON csit555.* TO 'db'@'%';
FLUSH PRIVILEGES; 