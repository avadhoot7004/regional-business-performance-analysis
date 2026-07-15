RETAIL_ANALYSIS_DBUSE ROLE ACCOUNTADMIN;

-- dedicated role for pipeline
CREATE ROLE IF NOT EXISTS RETAIL_ROLE;

-- compute warehouse
CREATE WAREHOUSE IF NOT EXISTS RETAIL_DATA_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Compute warehouse for retail analysis pipeline';

-- database
CREATE DATABASE IF NOT EXISTS RETAIL_ANALYSIS_DB
    COMMENT = 'Target database for superstore 3-medal schemas';

-- grant privileges to our new role
-- grant warehouse usage & operate start stop permissions
GRANT USAGE, OPERATE ON WAREHOUSE RETAIL_DATA_WH TO ROLE RETAIL_ROLE;

-- grant full privileges on the database
GRANT ALL PRIVILEGES ON DATABASE RETAIL_ANALYSIS_DB TO ROLE RETAIL_ROLE;

-- assign the role to active user, logged in user (admin)
GRANT ROLE RETAIL_ROLE TO USER admin;

-- sys admins can have visibility
GRANT ROLE RETAIL_ROLE TO ROLE SYSADMIN;

-- verify role assignment and initialize Medallion schemas
USE ROLE RETAIL_ROLE;
USE WAREHOUSE RETAIL_DATA_WH;
USE DATABASE RETAIL_ANALYSIS_DB;

-- create schemas representing 3 medal layers inside the new database
CREATE SCHEMA IF NOT EXISTS RETAIL_ANALYSIS_DB.SUPERSTORE_RAW; --bronze
CREATE SCHEMA IF NOT EXISTS RETAIL_ANALYSIS_DB.STG_SUPERSTORE; --silver
CREATE SCHEMA IF NOT EXISTS RETAIL_ANALYSIS_DB.MART_SUPERSTORE; --gold

-- Show schemas to verify successful creation
SHOW SCHEMAS IN DATABASE RETAIL_ANALYSIS_DB;
