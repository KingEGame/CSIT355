-- Create the user if it doesn't exist
ALTER USER 'db'@'%' IDENTIFIED WITH mysql_native_password BY 'csit_555';

-- Grant all privileges on csit_555 database to the user
GRANT ALL PRIVILEGES ON csit_555.* TO 'db'@'%';

-- Grant privileges needed for creating databases and users
GRANT CREATE, ALTER, DROP, REFERENCES ON *.* TO 'db'@'%';

-- Make the privileges take effect immediately
FLUSH PRIVILEGES; 