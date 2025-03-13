-- Setup Monitoring Schema for Data Quality and Cost Optimization
-- This script creates the necessary objects to track data quality and warehouse usage

-- Use the admin role to create the schema
USE ROLE MERCURIOS_ADMIN;
USE DATABASE MERCURIOS_DATA;

-- Create monitoring schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS MONITORING;

-- Switch to the monitoring schema
USE SCHEMA MONITORING;

-- Create table for data quality issues
CREATE OR REPLACE TABLE DATA_QUALITY_ISSUES (
    ISSUE_ID NUMBER IDENTITY(1,1),
    REPORT_ID VARCHAR(50),
    TABLE_NAME VARCHAR(255),
    COLUMN_NAME VARCHAR(255),
    CHECK_TYPE VARCHAR(50),
    SEVERITY VARCHAR(20),
    MESSAGE TEXT,
    TIMESTAMP TIMESTAMP_NTZ,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create table for warehouse usage metrics
CREATE OR REPLACE TABLE WAREHOUSE_USAGE_METRICS (
    METRIC_ID NUMBER IDENTITY(1,1),
    WAREHOUSE_NAME VARCHAR(255),
    START_TIME TIMESTAMP_NTZ,
    END_TIME TIMESTAMP_NTZ,
    CREDITS_USED FLOAT,
    QUERY_COUNT INTEGER,
    EXECUTION_TIME_MS INTEGER,
    BYTES_SCANNED INTEGER,
    ROWS_PRODUCED INTEGER,
    COMPILATION_TIME_MS INTEGER,
    QUEUED_PROVISIONING_TIME_MS INTEGER,
    QUEUED_REPAIR_TIME_MS INTEGER,
    QUEUED_OVERLOAD_TIME_MS INTEGER,
    BLOCKED_TIME_MS INTEGER,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create table for query performance metrics
CREATE OR REPLACE TABLE QUERY_PERFORMANCE_METRICS (
    QUERY_ID VARCHAR(50),
    WAREHOUSE_NAME VARCHAR(255),
    DATABASE_NAME VARCHAR(255),
    SCHEMA_NAME VARCHAR(255),
    QUERY_TEXT TEXT,
    USER_NAME VARCHAR(255),
    ROLE_NAME VARCHAR(255),
    EXECUTION_TIME_MS INTEGER,
    COMPILATION_TIME_MS INTEGER,
    BYTES_SCANNED INTEGER,
    ROWS_PRODUCED INTEGER,
    PARTITIONS_SCANNED INTEGER,
    PARTITIONS_TOTAL INTEGER,
    EXECUTION_STATUS VARCHAR(50),
    ERROR_CODE VARCHAR(50),
    ERROR_MESSAGE TEXT,
    START_TIME TIMESTAMP_NTZ,
    END_TIME TIMESTAMP_NTZ,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create table for materialized view candidates
CREATE OR REPLACE TABLE MATERIALIZED_VIEW_CANDIDATES (
    CANDIDATE_ID NUMBER IDENTITY(1,1),
    DATABASE_NAME VARCHAR(255),
    SCHEMA_NAME VARCHAR(255),
    QUERY_PATTERN TEXT,
    FREQUENCY INTEGER,
    TOTAL_EXECUTION_TIME_MS INTEGER,
    AVG_EXECUTION_TIME_MS INTEGER,
    BYTES_SCANNED INTEGER,
    ROWS_PRODUCED INTEGER,
    RECOMMENDATION TEXT,
    ESTIMATED_SAVINGS_CREDITS FLOAT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create table for clustering candidates
CREATE OR REPLACE TABLE CLUSTERING_CANDIDATES (
    CANDIDATE_ID NUMBER IDENTITY(1,1),
    DATABASE_NAME VARCHAR(255),
    SCHEMA_NAME VARCHAR(255),
    TABLE_NAME VARCHAR(255),
    COLUMN_NAMES VARCHAR(1000),
    FILTERING_RATIO FLOAT,
    QUERY_COUNT INTEGER,
    TOTAL_EXECUTION_TIME_MS INTEGER,
    AVG_EXECUTION_TIME_MS INTEGER,
    RECOMMENDATION TEXT,
    ESTIMATED_SAVINGS_CREDITS FLOAT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create table for credit usage by day
CREATE OR REPLACE TABLE DAILY_CREDIT_USAGE (
    USAGE_DATE DATE,
    WAREHOUSE_NAME VARCHAR(255),
    CREDITS_USED FLOAT,
    QUERY_COUNT INTEGER,
    AVERAGE_EXECUTION_TIME_MS INTEGER,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (USAGE_DATE, WAREHOUSE_NAME)
);

-- Create view to monitor warehouse performance
CREATE OR REPLACE VIEW WAREHOUSE_PERFORMANCE AS
SELECT
    WAREHOUSE_NAME,
    DATE_TRUNC('DAY', START_TIME) AS USAGE_DATE,
    SUM(CREDITS_USED) AS CREDITS_USED,
    COUNT(*) AS SESSION_COUNT,
    SUM(QUERY_COUNT) AS QUERY_COUNT,
    AVG(EXECUTION_TIME_MS) AS AVG_EXECUTION_TIME_MS,
    SUM(BYTES_SCANNED) / POWER(1024, 3) AS GB_SCANNED,
    SUM(ROWS_PRODUCED) AS ROWS_PRODUCED
FROM
    WAREHOUSE_USAGE_METRICS
GROUP BY
    WAREHOUSE_NAME, USAGE_DATE
ORDER BY
    USAGE_DATE DESC, CREDITS_USED DESC;

-- Create view to identify expensive queries
CREATE OR REPLACE VIEW EXPENSIVE_QUERIES AS
SELECT
    QUERY_ID,
    WAREHOUSE_NAME,
    DATABASE_NAME,
    SCHEMA_NAME,
    LEFT(QUERY_TEXT, 200) AS QUERY_TEXT_SAMPLE,
    USER_NAME,
    ROLE_NAME,
    EXECUTION_TIME_MS,
    BYTES_SCANNED / POWER(1024, 3) AS GB_SCANNED,
    ROWS_PRODUCED,
    START_TIME,
    END_TIME
FROM
    QUERY_PERFORMANCE_METRICS
WHERE
    EXECUTION_STATUS = 'SUCCESS'
ORDER BY
    EXECUTION_TIME_MS DESC
LIMIT 100;

-- Create view to monitor data quality trends
CREATE OR REPLACE VIEW DATA_QUALITY_TRENDS AS
SELECT
    DATE_TRUNC('DAY', TIMESTAMP) AS ISSUE_DATE,
    TABLE_NAME,
    CHECK_TYPE,
    SEVERITY,
    COUNT(*) AS ISSUE_COUNT
FROM
    DATA_QUALITY_ISSUES
GROUP BY
    ISSUE_DATE, TABLE_NAME, CHECK_TYPE, SEVERITY
ORDER BY
    ISSUE_DATE DESC, ISSUE_COUNT DESC;

-- Create stored procedure to populate warehouse usage metrics
CREATE OR REPLACE PROCEDURE POPULATE_WAREHOUSE_METRICS()
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // Query ACCOUNT_USAGE to get warehouse metrics
    var result = snowflake.execute({
        sqlText: `
            INSERT INTO MERCURIOS_DATA.MONITORING.WAREHOUSE_USAGE_METRICS (
                WAREHOUSE_NAME,
                START_TIME,
                END_TIME,
                CREDITS_USED,
                QUERY_COUNT,
                EXECUTION_TIME_MS,
                BYTES_SCANNED,
                ROWS_PRODUCED,
                COMPILATION_TIME_MS,
                QUEUED_PROVISIONING_TIME_MS,
                QUEUED_REPAIR_TIME_MS,
                QUEUED_OVERLOAD_TIME_MS,
                BLOCKED_TIME_MS
            )
            SELECT
                WAREHOUSE_NAME,
                START_TIME,
                END_TIME,
                CREDITS_USED,
                COUNT(QUERY_ID) AS QUERY_COUNT,
                SUM(TOTAL_ELAPSED_TIME) AS EXECUTION_TIME_MS,
                SUM(BYTES_SCANNED) AS BYTES_SCANNED,
                SUM(ROWS_PRODUCED) AS ROWS_PRODUCED,
                SUM(COMPILATION_TIME) AS COMPILATION_TIME_MS,
                SUM(QUEUED_PROVISIONING_TIME) AS QUEUED_PROVISIONING_TIME_MS,
                SUM(QUEUED_REPAIR_TIME) AS QUEUED_REPAIR_TIME_MS,
                SUM(QUEUED_OVERLOAD_TIME) AS QUEUED_OVERLOAD_TIME_MS,
                SUM(BLOCKED_TIME) AS BLOCKED_TIME_MS
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY w
            LEFT JOIN
                SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q
                ON q.WAREHOUSE_NAME = w.WAREHOUSE_NAME
                AND q.START_TIME BETWEEN w.START_TIME AND w.END_TIME
            WHERE
                w.START_TIME >= DATEADD(DAY, -1, CURRENT_TIMESTAMP())
                AND w.START_TIME > (SELECT MAX(END_TIME) FROM MERCURIOS_DATA.MONITORING.WAREHOUSE_USAGE_METRICS)
            GROUP BY
                w.WAREHOUSE_NAME, w.START_TIME, w.END_TIME, w.CREDITS_USED
        `
    });
    
    // Return success message
    return "Warehouse metrics updated successfully";
$$;

-- Create stored procedure to populate query performance metrics
CREATE OR REPLACE PROCEDURE POPULATE_QUERY_METRICS()
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // Query ACCOUNT_USAGE to get query metrics
    var result = snowflake.execute({
        sqlText: `
            INSERT INTO MERCURIOS_DATA.MONITORING.QUERY_PERFORMANCE_METRICS (
                QUERY_ID,
                WAREHOUSE_NAME,
                DATABASE_NAME,
                SCHEMA_NAME,
                QUERY_TEXT,
                USER_NAME,
                ROLE_NAME,
                EXECUTION_TIME_MS,
                COMPILATION_TIME_MS,
                BYTES_SCANNED,
                ROWS_PRODUCED,
                PARTITIONS_SCANNED,
                PARTITIONS_TOTAL,
                EXECUTION_STATUS,
                ERROR_CODE,
                ERROR_MESSAGE,
                START_TIME,
                END_TIME
            )
            SELECT
                QUERY_ID,
                WAREHOUSE_NAME,
                DATABASE_NAME,
                SCHEMA_NAME,
                QUERY_TEXT,
                USER_NAME,
                ROLE_NAME,
                TOTAL_ELAPSED_TIME AS EXECUTION_TIME_MS,
                COMPILATION_TIME AS COMPILATION_TIME_MS,
                BYTES_SCANNED,
                ROWS_PRODUCED,
                PARTITIONS_SCANNED,
                PARTITIONS_TOTAL,
                EXECUTION_STATUS,
                ERROR_CODE,
                ERROR_MESSAGE,
                START_TIME,
                END_TIME
            FROM
                SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
            WHERE
                START_TIME >= DATEADD(DAY, -1, CURRENT_TIMESTAMP())
                AND QUERY_ID NOT IN (SELECT QUERY_ID FROM MERCURIOS_DATA.MONITORING.QUERY_PERFORMANCE_METRICS)
        `
    });
    
    // Return success message
    return "Query metrics updated successfully";
$$;

-- Create stored procedure to populate daily credit usage
CREATE OR REPLACE PROCEDURE POPULATE_DAILY_CREDIT_USAGE()
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // Query ACCOUNT_USAGE to get daily credit usage
    var result = snowflake.execute({
        sqlText: `
            MERGE INTO MERCURIOS_DATA.MONITORING.DAILY_CREDIT_USAGE t
            USING (
                SELECT
                    DATE_TRUNC('DAY', START_TIME) AS USAGE_DATE,
                    WAREHOUSE_NAME,
                    SUM(CREDITS_USED) AS CREDITS_USED,
                    COUNT(DISTINCT QUERY_ID) AS QUERY_COUNT,
                    AVG(TOTAL_ELAPSED_TIME) AS AVERAGE_EXECUTION_TIME_MS
                FROM
                    SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY w
                LEFT JOIN
                    SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q
                    ON q.WAREHOUSE_NAME = w.WAREHOUSE_NAME
                    AND q.START_TIME BETWEEN w.START_TIME AND w.END_TIME
                WHERE
                    w.START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
                GROUP BY
                    USAGE_DATE, w.WAREHOUSE_NAME
            ) s
            ON t.USAGE_DATE = s.USAGE_DATE AND t.WAREHOUSE_NAME = s.WAREHOUSE_NAME
            WHEN MATCHED THEN
                UPDATE SET
                    t.CREDITS_USED = s.CREDITS_USED,
                    t.QUERY_COUNT = s.QUERY_COUNT,
                    t.AVERAGE_EXECUTION_TIME_MS = s.AVERAGE_EXECUTION_TIME_MS,
                    t.CREATED_AT = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (USAGE_DATE, WAREHOUSE_NAME, CREDITS_USED, QUERY_COUNT, AVERAGE_EXECUTION_TIME_MS)
                VALUES (s.USAGE_DATE, s.WAREHOUSE_NAME, s.CREDITS_USED, s.QUERY_COUNT, s.AVERAGE_EXECUTION_TIME_MS)
        `
    });
    
    // Return success message
    return "Daily credit usage updated successfully";
$$;

-- Create stored procedure to identify materialized view candidates
CREATE OR REPLACE PROCEDURE IDENTIFY_MATERIALIZED_VIEW_CANDIDATES()
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // Query ACCOUNT_USAGE to find repeated query patterns
    var result = snowflake.execute({
        sqlText: `
            INSERT INTO MERCURIOS_DATA.MONITORING.MATERIALIZED_VIEW_CANDIDATES (
                DATABASE_NAME,
                SCHEMA_NAME,
                QUERY_PATTERN,
                FREQUENCY,
                TOTAL_EXECUTION_TIME_MS,
                AVG_EXECUTION_TIME_MS,
                BYTES_SCANNED,
                ROWS_PRODUCED,
                RECOMMENDATION,
                ESTIMATED_SAVINGS_CREDITS
            )
            WITH repeated_queries AS (
                SELECT
                    DATABASE_NAME,
                    SCHEMA_NAME,
                    REGEXP_REPLACE(QUERY_TEXT, '\\d+', '?') AS QUERY_PATTERN,
                    COUNT(*) AS FREQUENCY,
                    SUM(TOTAL_ELAPSED_TIME) AS TOTAL_EXECUTION_TIME_MS,
                    AVG(TOTAL_ELAPSED_TIME) AS AVG_EXECUTION_TIME_MS,
                    SUM(BYTES_SCANNED) AS BYTES_SCANNED,
                    SUM(ROWS_PRODUCED) AS ROWS_PRODUCED
                FROM
                    SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
                WHERE
                    EXECUTION_STATUS = 'SUCCESS'
                    AND TOTAL_ELAPSED_TIME > 1000 -- Only queries taking more than 1 second
                    AND QUERY_TYPE = 'SELECT'
                    AND START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
                GROUP BY
                    DATABASE_NAME, SCHEMA_NAME, QUERY_PATTERN
                HAVING
                    COUNT(*) >= 10 -- Only patterns that appear at least 10 times
                    AND AVG(TOTAL_ELAPSED_TIME) > 2000 -- Average execution time > 2 seconds
            )
            SELECT
                DATABASE_NAME,
                SCHEMA_NAME,
                QUERY_PATTERN,
                FREQUENCY,
                TOTAL_EXECUTION_TIME_MS,
                AVG_EXECUTION_TIME_MS,
                BYTES_SCANNED,
                ROWS_PRODUCED,
                'Consider creating a materialized view for this query pattern to improve performance' AS RECOMMENDATION,
                (FREQUENCY * AVG_EXECUTION_TIME_MS / 1000 / 3600) * 0.5 AS ESTIMATED_SAVINGS_CREDITS -- Rough estimate
            FROM
                repeated_queries
            WHERE
                QUERY_PATTERN NOT IN (SELECT QUERY_PATTERN FROM MERCURIOS_DATA.MONITORING.MATERIALIZED_VIEW_CANDIDATES)
            ORDER BY
                TOTAL_EXECUTION_TIME_MS DESC
            LIMIT 20
        `
    });
    
    // Return success message
    return "Materialized view candidates identified successfully";
$$;

-- Create stored procedure to identify clustering candidates
CREATE OR REPLACE PROCEDURE IDENTIFY_CLUSTERING_CANDIDATES()
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // Query ACCOUNT_USAGE to find tables that would benefit from clustering
    var result = snowflake.execute({
        sqlText: `
            INSERT INTO MERCURIOS_DATA.MONITORING.CLUSTERING_CANDIDATES (
                DATABASE_NAME,
                SCHEMA_NAME,
                TABLE_NAME,
                COLUMN_NAMES,
                FILTERING_RATIO,
                QUERY_COUNT,
                TOTAL_EXECUTION_TIME_MS,
                AVG_EXECUTION_TIME_MS,
                RECOMMENDATION,
                ESTIMATED_SAVINGS_CREDITS
            )
            WITH table_scans AS (
                SELECT
                    q.DATABASE_NAME,
                    q.SCHEMA_NAME,
                    o.TABLE_NAME,
                    LISTAGG(DISTINCT f.VALUE::STRING, ', ') WITHIN GROUP (ORDER BY f.VALUE::STRING) AS COLUMN_NAMES,
                    AVG(PARTITIONS_SCANNED / NULLIF(PARTITIONS_TOTAL, 0)) AS FILTERING_RATIO,
                    COUNT(*) AS QUERY_COUNT,
                    SUM(TOTAL_ELAPSED_TIME) AS TOTAL_EXECUTION_TIME_MS,
                    AVG(TOTAL_ELAPSED_TIME) AS AVG_EXECUTION_TIME_MS
                FROM
                    SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q,
                    LATERAL FLATTEN(input => PARSE_JSON(OBJECTS_MODIFIED)) o,
                    LATERAL FLATTEN(input => PARSE_JSON(FILTERS)) f
                WHERE
                    q.EXECUTION_STATUS = 'SUCCESS'
                    AND o.VALUE:objectDomain::STRING = 'Table'
                    AND q.START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
                GROUP BY
                    q.DATABASE_NAME, q.SCHEMA_NAME, o.TABLE_NAME
                HAVING
                    COUNT(*) >= 5 -- Only tables queried at least 5 times
                    AND AVG_EXECUTION_TIME_MS > 5000 -- Average execution time > 5 seconds
                    AND FILTERING_RATIO < 0.5 -- Scanning less than 50% of partitions
            )
            SELECT
                DATABASE_NAME,
                SCHEMA_NAME,
                TABLE_NAME,
                COLUMN_NAMES,
                FILTERING_RATIO,
                QUERY_COUNT,
                TOTAL_EXECUTION_TIME_MS,
                AVG_EXECUTION_TIME_MS,
                'Consider clustering this table on columns: ' || COLUMN_NAMES AS RECOMMENDATION,
                (QUERY_COUNT * AVG_EXECUTION_TIME_MS / 1000 / 3600) * (1 - FILTERING_RATIO) * 0.3 AS ESTIMATED_SAVINGS_CREDITS -- Rough estimate
            FROM
                table_scans
            WHERE
                (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME) NOT IN (
                    SELECT DATABASE_NAME, SCHEMA_NAME, TABLE_NAME FROM MERCURIOS_DATA.MONITORING.CLUSTERING_CANDIDATES
                )
            ORDER BY
                TOTAL_EXECUTION_TIME_MS DESC
            LIMIT 20
        `
    });
    
    // Return success message
    return "Clustering candidates identified successfully";
$$;

-- Create task to run the warehouse metrics procedure daily
CREATE OR REPLACE TASK TASK_POPULATE_WAREHOUSE_METRICS
    WAREHOUSE = MERCURIOS_ANALYTICS_WH
    SCHEDULE = 'USING CRON 0 1 * * * UTC'
AS
    CALL POPULATE_WAREHOUSE_METRICS();

-- Create task to run the query metrics procedure daily
CREATE OR REPLACE TASK TASK_POPULATE_QUERY_METRICS
    WAREHOUSE = MERCURIOS_ANALYTICS_WH
    SCHEDULE = 'USING CRON 15 1 * * * UTC'
AS
    CALL POPULATE_QUERY_METRICS();

-- Create task to run the daily credit usage procedure daily
CREATE OR REPLACE TASK TASK_POPULATE_DAILY_CREDIT_USAGE
    WAREHOUSE = MERCURIOS_ANALYTICS_WH
    SCHEDULE = 'USING CRON 30 1 * * * UTC'
AS
    CALL POPULATE_DAILY_CREDIT_USAGE();

-- Create task to identify materialized view candidates weekly
CREATE OR REPLACE TASK TASK_IDENTIFY_MATERIALIZED_VIEW_CANDIDATES
    WAREHOUSE = MERCURIOS_ANALYTICS_WH
    SCHEDULE = 'USING CRON 0 2 * * 1 UTC' -- Run every Monday at 2 AM UTC
AS
    CALL IDENTIFY_MATERIALIZED_VIEW_CANDIDATES();

-- Create task to identify clustering candidates weekly
CREATE OR REPLACE TASK TASK_IDENTIFY_CLUSTERING_CANDIDATES
    WAREHOUSE = MERCURIOS_ANALYTICS_WH
    SCHEDULE = 'USING CRON 30 2 * * 1 UTC' -- Run every Monday at 2:30 AM UTC
AS
    CALL IDENTIFY_CLUSTERING_CANDIDATES();

-- Resume all tasks
ALTER TASK TASK_POPULATE_WAREHOUSE_METRICS RESUME;
ALTER TASK TASK_POPULATE_QUERY_METRICS RESUME;
ALTER TASK TASK_POPULATE_DAILY_CREDIT_USAGE RESUME;
ALTER TASK TASK_IDENTIFY_MATERIALIZED_VIEW_CANDIDATES RESUME;
ALTER TASK TASK_IDENTIFY_CLUSTERING_CANDIDATES RESUME;

-- Grant permissions
GRANT USAGE ON SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_DEVELOPER;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_DEVELOPER;
GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_DEVELOPER;

GRANT USAGE ON SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_ANALYST;
GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_ANALYST;
