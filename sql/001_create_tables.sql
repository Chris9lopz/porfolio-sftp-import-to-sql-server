/*
Create the consolidated and audit tables.

Before running this script, replace the business columns in dbo.sftp_data_consolidated
with the real CSV schema. Keep the technical metadata columns.
*/

IF OBJECT_ID('dbo.sftp_data_consolidated', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.sftp_data_consolidated (
        agent_id INT NOT NULL,
		first_name VARCHAR(255),
		last_name VARCHAR(255),
		email VARCHAR(255),
		gender VARCHAR(255),
		title VARCHAR(255),
		country VARCHAR(255),
		phone VARCHAR(255),
        source_file_name VARCHAR(255) NOT NULL,
        source_file_path VARCHAR(1000) NOT NULL,
        source_file_size_bytes BIGINT NOT NULL,
        imported_at DATETIME2(3) NOT NULL
    );
END;
GO

IF OBJECT_ID('dbo.sftp_import_audit', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.sftp_import_audit (
        audit_id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        source_file_name VARCHAR(255) NOT NULL,
        source_file_path VARCHAR(1000) NOT NULL,
        source_file_size_bytes BIGINT NULL,
        status VARCHAR(30) NOT NULL,
        rows_inserted BIGINT NULL,
        started_at DATETIME2(3) NOT NULL,
        finished_at DATETIME2(3) NULL,
        error_message VARCHAR(MAX) NULL
    );
END;
GO
