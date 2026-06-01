# SFTP to SQL Server ETL Pipeline

## Project Overview

This project demonstrates the development of an automated ETL (Extract, Transform, Load) pipeline using Python. The solution retrieves files from a secure SFTP server, processes and validates the data, and loads the results into Microsoft SQL Server for reporting and analytics purposes.

The project simulates a common enterprise data engineering scenario where data is received from external providers through secure file transfers and must be integrated into a centralized database.

## Business Problem

Organizations often receive data files from third-party vendors through SFTP servers. Manual downloads and database imports are time-consuming, error-prone, and difficult to scale.

This project automates the entire process by:

1. Connecting securely to an SFTP server.
2. Downloading incoming files.
3. Validating and transforming the data.
4. Loading the processed information into SQL Server.
5. Logging execution details and handling failures.

## Solution Architecture

```text
+----------------+
|  SFTP Server   |
+----------------+
        |
        v
+----------------+
| File Download  |
+----------------+
        |
        v
+----------------------+
| Data Validation &    |
| Transformation       |
+----------------------+
        |
        v
+----------------+
|  SQL Server    |
+----------------+
```

## Key Features

* Secure SFTP connectivity
* Automated file ingestion
* Data validation and cleansing
* SQL Server integration
* Error handling and logging
* Configurable environment settings
* Reusable ETL architecture

## Technologies Used

| Technology          | Purpose                            |
| ------------------- | ---------------------------------- |
| Python              | ETL development                    |
| Paramiko            | SFTP connection and file transfer  |
| Pandas              | Data processing and transformation |
| SQL Server          | Data storage                       |
| SQLAlchemy / PyODBC | Database connectivity              |
| Logging             | Monitoring and troubleshooting     |

## ETL Process

### Extract

* Establishes a secure connection to the SFTP server.
* Downloads source files from a configured directory.

### Transform

* Reads and validates incoming data.
* Handles data quality checks.
* Applies business transformations.
* Prepares records for database insertion.

### Load

* Connects to SQL Server.
* Inserts or updates records in target tables.
* Generates execution logs for auditing purposes.

## Engineering Considerations

During development, special attention was given to:

* Separation of concerns between extraction, transformation, and loading layers.
* Error recovery and exception handling.
* Configuration-driven design.
* Maintainability and scalability.
* Secure credential management practices.

## Skills Demonstrated

This project showcases practical experience in:

* Data Engineering
* ETL Pipeline Development
* Python Programming
* SQL Development
* Database Integration
* Data Validation
* Automation
* Enterprise Data Workflows

## Future Improvements

Potential enhancements include:

* Incremental data loading.
* Docker containerization.
* Workflow orchestration with Apache Airflow.
* Automated testing.
* Cloud deployment.
* Monitoring and alerting.

## Author

Christian López

Data Engineer | Python Developer | Data Science Student
