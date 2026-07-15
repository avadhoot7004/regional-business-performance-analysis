import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv


# load variables from .env file into environment variables
load_dotenv()

SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}


def get_snowflake_connection(config: dict):
    required_keys = ["account", "user", "password", "warehouse", "database", "schema", "role"]

    missing = [
        key for key in required_keys
        if not config.get(key) or str(config.get(key)).startswith("<")
    ]

    if missing:
        raise ValueError(f"Missing Snowflake config values: {missing}")

    conn = snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        password=config["password"],
        warehouse=config["warehouse"], 
        database=config["database"], 
        schema=config["schema"],
        role=config["role"],
    )

    return conn

def load_data_to_snowflake():
    # load CSV data
    csv_path = "data/raw/superstore.csv"
    print(f"Reading local CSV file: {csv_path}...")
    df = pd.read_csv(csv_path, encoding='latin1')
    
    # standardize column headers to uppercase (Snowflake default), replace spaces/hyphens with underscores, and strip outer spaces
    df.columns = [c.strip().upper().replace(' ', '_').replace('-', '_') for c in df.columns]
    
    # get connection credentials and connect
    db_name = SNOWFLAKE_CONFIG['database'].upper()
    print(f"Connecting to Snowflake database '{db_name}' as user '{SNOWFLAKE_CONFIG['user']}'...")
    conn = get_snowflake_connection(SNOWFLAKE_CONFIG)


    
    try:
        cursor = conn.cursor()
        
        # verify schemas for medallion architecture exist in the database
        schemas = ['SUPERSTORE_RAW', 'STG_SUPERSTORE', 'MART_SUPERSTORE']
        cursor.execute(f"SHOW SCHEMAS IN DATABASE {db_name}")
        existing_schemas = [row[1].upper() for row in cursor.fetchall()]
        
        missing_schemas = [s for s in schemas if s not in existing_schemas]
        if missing_schemas:
            raise ValueError(
                f"Missing required Medallion schemas in database '{db_name}': {missing_schemas}. "
                f"Please execute the setup script (scripts/setup_snowflake.sql) in Snowflake first."
            )
        print(f"Verification: All required Medallion schemas {schemas} exist.")

        
        # define raw orders table structure in RAW schema
        # we store columns in superstore_raw exactly as strings or numeric types as they come
        raw_table_name = "ORDERS"
        print(f"Creating raw table {db_name}.SUPERSTORE_RAW.{raw_table_name}...")
        
        cursor.execute(f"""
            CREATE OR REPLACE TABLE {db_name}.SUPERSTORE_RAW.{raw_table_name} (
                ROW_ID INT,
                ORDER_ID VARCHAR,
                ORDER_DATE VARCHAR,
                SHIP_DATE VARCHAR,
                SHIP_MODE VARCHAR,
                CUSTOMER_ID VARCHAR,
                CUSTOMER_NAME VARCHAR,
                SEGMENT VARCHAR,
                COUNTRY VARCHAR,
                CITY VARCHAR,
                STATE VARCHAR,
                POSTAL_CODE INT,
                REGION VARCHAR,
                PRODUCT_ID VARCHAR,
                CATEGORY VARCHAR,
                SUB_CATEGORY VARCHAR,
                PRODUCT_NAME VARCHAR,
                SALES FLOAT,
                QUANTITY INT,
                DISCOUNT FLOAT,
                PROFIT FLOAT
            )
        """)
        
        # load data using write_pandas by using internal staging + copy_into
        print(f"Loading {len(df)} rows into {db_name}.SUPERSTORE_RAW.{raw_table_name} using write_pandas...")

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=raw_table_name,
            database=db_name,
            schema="SUPERSTORE_RAW"
        )
        
        if success:
            print(f"Success! Loaded {nrows} rows in {nchunks} chunks.")
            
            # row cont for validation of the loaded dataset
            cursor.execute(f"SELECT COUNT(*) FROM {db_name}.SUPERSTORE_RAW.{raw_table_name}")
            db_row_count = cursor.fetchone()[0]
            print(f"Verification: Found {db_row_count} rows in Snowflake table.")
        else:
            print("Failed to load data into Snowflake.")
            
        cursor.close()
    except Exception as e:
        print("Error loading data to Snowflake:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    load_data_to_snowflake()
