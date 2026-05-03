-- Run this script as the 'system' or 'sys' user connected to your FREEPDB1 pluggable database.
-- Example connection string: sqlplus system/your_password@localhost:1521/FREEPDB1

-- Create a dedicated user for the RAG application
CREATE USER raguser IDENTIFIED BY "password123456" DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;

-- Grant necessary privileges
GRANT CONNECT, RESOURCE TO raguser;

-- Optional: If the RESOURCE role does not automatically grant CREATE VIEW or other specific privileges in your version, grant them explicitly
GRANT CREATE VIEW TO raguser;
