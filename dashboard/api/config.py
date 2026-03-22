from pathlib import Path
from dotenv import load_dotenv # ignore
import os
# import toml

# from trading_engine import config


# if Path.cwd().name == "dashboard":
#     config_path = Path.cwd() / ".streamlit" / "config.toml"
# else:
#     config_path  = Path.cwd() / "dashboard" / ".streamlit" / "config.toml"
# config = toml.load(config_path)
    
# API_URL = config['api-dev']['url']

load_dotenv()

if os.getenv("ENVIRONMENT") == "production":
    API_URL = os.getenv("API_URL")
else:
    API_URL = os.getenv("API_URL_DEV")