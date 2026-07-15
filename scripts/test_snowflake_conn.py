import snowflake.connector
import yaml
import os

def load_credentials():
    profile_path = os.path.expanduser("~/.dbt/profiles.yml")
    with open(profile_path, "r") as f:
        config = yaml.safe_load(f)
    
    dev_config = config['superstore_analytics']['outputs']['dev']
    return dev_config


def test_connection():
    creds = load_credentials()
    print("Connecting to Snowflake account:", creds['account'])
    
    try:
        conn = snowflake.connector.connect(
            user=creds['user'],
            password=creds['password'],
            account=creds['account'],
            warehouse=creds['warehouse'],
            role=creds['role']
        )
        print("Successfully connected to Snowflake!")
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT CURRENT_VERSION(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
        version, role, wh = cursor.fetchone()
        print(f"Snowflake Version: {version}")
        print(f"Current Role: {role}")
        print(f"Current Warehouse: {wh}")
        
        # Check permissions by listing databases
        cursor.execute("SHOW DATABASES")
        dbs = [row[1] for row in cursor.fetchall()]
        print("Available Databases:", dbs)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print("Snowflake connection failed:", e)

if __name__ == "__main__":
    test_connection()
