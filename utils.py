import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_config(config_path="config.json"):
    """
    Load configuration from a JSON file.
    
    Args:
        config_path (str): Path to the config file. Defaults to 'config.json'.
    
    Returns:
        dict: Configuration dictionary, or empty dict if file not found/error.
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        else:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
    except Exception as e:
        logger.error(f"Error loading config {config_path}: {str(e)}")
        return {}

def save_config(config, config_path="config.json"):
    """
    Save configuration to a JSON file.
    
    Args:
        config (dict): Configuration dictionary to save.
        config_path (str): Path to save the config file. Defaults to 'config.json'.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config {config_path}: {str(e)}")
        return False

def read_python_file(file_path):
    """
    Read content of a Python file.
    
    Args:
        file_path (str): Path to the Python file.
    
    Returns:
        str: File content, or empty string if error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"Read file {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""

def write_python_file(content, file_path):
    """
    Write content to a Python file.
    
    Args:
        content (str): Content to write.
        file_path (str): Path to the output file.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Wrote file {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {str(e)}")
        return False

def ensure_directory(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory (str): Directory path.
    
    Returns:
        bool: True if directory exists or was created, False otherwise.
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory {directory} exists")
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {str(e)}")
        return False