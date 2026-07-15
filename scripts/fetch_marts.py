import os
import snowflake.connector
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

def fetch_results():
    conn = get_snowflake_connection(SNOWFLAKE_CONFIG)
    
    cursor = conn.cursor()
    db_name = SNOWFLAKE_CONFIG['database'].upper()
    for table in ['MART_REGION_SALES', 'MART_REGION_PROFIT', 'MART_CUSTOMER_SEGMENT', 'MART_TOP_REGION']:
        print(f"\n========================================\n=== {table} ===\n========================================")
        cursor.execute(f"SELECT * FROM {db_name}.MART_SUPERSTORE.{table}")


        cols = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        # formatting results in markdown table
        print("| " + " | ".join(cols) + " |")
        print("| " + " | ".join(["---"] * len(cols)) + " |")
        for r in rows:
            print("| " + " | ".join([str(val) for val in r]) + " |")
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_results()
