import os
import sys
import subprocess

def load_env():
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip("'").strip('"')
                    os.environ[key.strip()] = val
        print("Loaded connection variables from .env")
    else:
        print("Warning: .env file not found!")

def run_dbt():
    load_env()
    
    # Locate local virtual environment dbt executable
    venv_dbt = os.path.join(".venv", "Scripts", "dbt.exe")
    if os.path.exists(venv_dbt):
        dbt_exe = venv_dbt
    else:
        dbt_exe = "dbt" # Fallback

        
    args = sys.argv[1:]
    # Force profiles-dir to be the current directory
    cmd = [dbt_exe] + args + ["--profiles-dir", "."]
    
    print("Executing:", " ".join(cmd))
    try:
        # Use shell=True for windows execution compatibility
        result = subprocess.run(cmd, shell=True)
        sys.exit(result.returncode)
    except Exception as e:
        print("Error executing dbt wrapper:", e)
        sys.exit(1)

if __name__ == "__main__":
    run_dbt()
