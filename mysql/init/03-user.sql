-- Remove the wrong user if exists
DROP USER IF EXISTS 'db'@'localhost';

-- Create a user that can connect from anywhere
CREATE USER IF NOT EXISTS 'db'@'%' IDENTIFIED BY 'csit_555';
GRANT ALL PRIVILEGES ON *.* TO 'db'@'%' WITH GRANT OPTION;

-- Optional: create also for localhost
CREATE USER IF NOT EXISTS 'db'@'localhost' IDENTIFIED BY 'csit_555';
GRANT ALL PRIVILEGES ON *.* TO 'db'@'localhost' WITH GRANT OPTION;

FLUSH PRIVILEGES;
