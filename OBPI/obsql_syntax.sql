-- OBSQL Syntax Definition

-- Table Creation
CREATE TABLE tablename (
    column_name type [CONSTRAINTS],
    ...
) [STORAGE_OPTIONS];

-- Storage Options
STORAGE_OPTIONS ::= 
    STORAGE_TYPE = ('MEMORY' | 'PEPX' | 'DISTRIBUTED')
    [, COMPRESSION = ('NONE' | 'LZ4' | 'ZSTD')]
    [, ENCRYPTION = ('NONE' | 'AES256')]
    [, REPLICATION = integer]

-- Custom Types
CREATE TYPE typename AS (
    field_name type,
    ...
);

-- Views
CREATE VIEW viewname AS
SELECT ...
WITH STORAGE = ('MEMORY' | 'PEPX');

-- Procedures
CREATE PROCEDURE procname(param type, ...)
SECURITY (USER | SYSTEM)
AS BEGIN
    -- OBPL code can be embedded here
    #[obpl]
    func processData(data: string) -> bool {
        // Process data
        return true;
    }
    #[end]
END;

-- Triggers
CREATE TRIGGER triggername
(BEFORE | AFTER) (INSERT | UPDATE | DELETE)
ON tablename
EXECUTE PROCEDURE procname();

-- Example OBSQL code:
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(64) UNIQUE,
    password_hash BYTES(32),
    created_at TIMESTAMP DEFAULT NOW()
) STORAGE_TYPE = 'PEPX',
  COMPRESSION = 'ZSTD',
  ENCRYPTION = 'AES256';

CREATE PROCEDURE verify_user(
    username VARCHAR,
    password VARCHAR
) SECURITY SYSTEM
AS BEGIN
    #[obpl]
    func hashPassword(pwd: string) -> bytes {
        return crypto.sha256(pwd);
    }
    #[end]
    
    DECLARE hash BYTES(32);
    SET hash = hashPassword(password);
    
    SELECT COUNT(*) FROM users
    WHERE username = @username
    AND password_hash = hash;
END;