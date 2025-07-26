import json
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Email configuration
        self.email_sender = os.getenv("EMAIL_SENDER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_recipient = os.getenv("EMAIL_RECIPIENT", self.email_sender)
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        # Scraping configuration
        self.check_interval_hours = int(os.getenv("CHECK_INTERVAL_HOURS", "24"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))
        
        # Validate required configuration
        if not self.email_sender or not self.email_password:
            raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD must be set in environment variables")

    def load_keywords(self, filename='data/keywords.json'):
        """Load keywords from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading keywords: {e}")
            return []
            
    def load_team_urls(self, filename='data/team_urls.json'):
        """Load team URLs from JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading team URLs: {e}")
            return {}
        