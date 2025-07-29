import json
import logging
import os
from datetime import datetime
import hashlib

def setup_logging(log_dir='logs'):
    """Set up logging configuration"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, f'nba_scraper_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def load_json_file(filename, default=None):
    """Load data from a JSON file with error handling"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"File {filename} not found, using default value")
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON from {filename}: {e}")
        return default if default is not None else {}

def save_json_file(data, filename):
    """Save data to a JSON file with error handling"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")
        return False

def generate_job_hash(job_data):
    """Generate a unique hash for a job posting to detect duplicates"""
    # Create a string from key job information
    job_string = f"{job_data.get('team', '')}{job_data.get('title', '')}{job_data.get('url', '')}"
    return hashlib.md5(job_string.encode()).hexdigest()

def filter_duplicate_jobs(jobs, seen_hashes=None):
    """Remove duplicate job postings based on generated hashes"""
    if seen_hashes is None:
        seen_hashes = set()
    
    unique_jobs = []
    
    for job in jobs:
        job_hash = generate_job_hash(job)
        if job_hash not in seen_hashes:
            seen_hashes.add(job_hash)
            unique_jobs.append(job)
            
    logging.info(f"Filtered {len(jobs) - len(unique_jobs)} duplicate jobs")
    return unique_jobs, seen_hashes

def validate_email_config(config):
    """Validate email configuration"""
    required_fields = ['email_sender', 'email_password', 'smtp_server', 'smtp_port']
    
    for field in required_fields:
        if not hasattr(config, field) or not getattr(config, field):
            raise ValueError(f"Missing required email configuration: {field}")
    
    return True

def clean_text(text):
    """Clean and normalize text for better keyword matching"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    return ' '.join(text.split()).strip()

def is_valid_url(url):
    """Basic URL validation"""
    return url and (url.startswith('http://') or url.startswith('https://'))

def create_backup_file(filename):
    """Create a backup of an existing file"""
    if os.path.exists(filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename}.backup_{timestamp}"
        
        try:
            with open(filename, 'r') as original:
                with open(backup_filename, 'w') as backup:
                    backup.write(original.read())
            logging.info(f"Backup created: {backup_filename}")
            return backup_filename
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
    
    return None

def get_project_root():
    """Get the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_directories_exist():
    """Ensure required directories exist"""
    root = get_project_root()
    directories = ['logs', 'data']
    
    for directory in directories:
        dir_path = os.path.join(root, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info(f"Created directory: {dir_path}")
            
def log_message(message, log_file='logs/app.log'):
    import logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    logging.info(message)