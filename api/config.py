"""
Database configuration and connection utilities
Supports both SQLite (dev) and PostgreSQL (prod)
Configuration loaded from config.yaml
"""
import os
import yaml
import re
from pathlib import Path

def _expand_env_vars(value):
    """Expand environment variables in config values.
    Format: ${VAR_NAME:default_value} or ${VAR_NAME}
    """
    if not isinstance(value, str):
        return value
    
    # Pattern: ${VAR_NAME:default} or ${VAR_NAME}
    pattern = r'\$\{([^:}]+)(?::([^}]*))?\}'
    
    def replacer(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) is not None else ''
        return os.getenv(var_name, default_value)
    
    return re.sub(pattern, replacer, value)

def _load_config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent / 'config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get environment from env var or use default from config
    environment = os.getenv('ENVIRONMENT', config.get('default_environment', 'development'))
    
    # Get environment-specific config
    env_config = config.get(environment, {})
    db_config = env_config.get('database', {})
    
    # Expand environment variables in all string values
    expanded_config = {}
    for key, value in db_config.items():
        expanded_config[key] = _expand_env_vars(value)
    
    return environment, expanded_config

# Load configuration
ENVIRONMENT, _db_config = _load_config()
DATABASE_TYPE = _db_config.get('type', 'sqlite')

# Set variables based on database type
if DATABASE_TYPE == 'sqlite':
    SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), _db_config.get('path', '../db/stocks_db.db'))
    POSTGRES_HOST = None
    POSTGRES_PORT = None
    POSTGRES_DB = None
    POSTGRES_USER = None
    POSTGRES_PASSWORD = None
else:
    SQLITE_DB_PATH = None
    POSTGRES_HOST = _db_config.get('host', 'postgres-service')
    POSTGRES_PORT = _db_config.get('port', '5432')
    POSTGRES_DB = _db_config.get('database', 'stockster')
    POSTGRES_USER = _db_config.get('user', 'stockster')
    POSTGRES_PASSWORD = _db_config.get('password', '')

# API configuration
API_HOST = os.environ.get('API_HOST', '0.0.0.0')
API_PORT = int(os.environ.get('API_PORT', '8000'))

def get_config():
    """Get current configuration"""
    return {
        'environment': ENVIRONMENT,
        'database_type': DATABASE_TYPE,
        'sqlite_path': SQLITE_DB_PATH if DATABASE_TYPE == 'sqlite' else None,
        'postgres_host': POSTGRES_HOST if DATABASE_TYPE == 'postgresql' else None,
    }
