import os
import sys
import unittest
from unittest.mock import patch, MagicMock
# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.email_sender import EmailSender
from src.config import Config

class TestEmailSender(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.email_sender = EmailSender(self.config)
        
        # Sample job data with all required fields
        self.sample_jobs = {
            "Lakers": [
                {
                    "title": "Assistant Coach", 
                    "team": "Lakers",
                    "url": "http://lakers.com/jobs/assistant-coach",
                    "scraped_at": "2025-07-23 10:00:00"
                }
            ],
            "Celtics": [
                {
                    "title": "Data Analyst", 
                    "team": "Celtics",
                    "url": "http://celtics.com/jobs/data-analyst",
                    "scraped_at": "2025-07-23 10:00:00"
                },
                {
                    "title": "Marketing Manager", 
                    "team": "Celtics",
                    "url": "http://celtics.com/jobs/marketing-manager",
                    "scraped_at": "2025-07-23 10:00:00"
                }
            ]
        }

    def test_format_job_listings_email(self):
        """Test that job listings are formatted correctly for email"""
        # Call the internal formatting method
        formatted_email = self.email_sender._format_job_listings_email(
            self.sample_jobs, 
            total_jobs=3
        )
        
        # Check that the email contains expected content
        self.assertIn("NBA Career Opportunities Report", formatted_email)
        self.assertIn("Total Jobs Found: 3", formatted_email)
        self.assertIn("LAKERS (1 jobs)", formatted_email)
        self.assertIn("CELTICS (2 jobs)", formatted_email)
        self.assertIn("📋 Title: Assistant Coach", formatted_email)
        self.assertIn("📋 Title: Data Analyst", formatted_email)
        self.assertIn("📋 Title: Marketing Manager", formatted_email)
        self.assertIn("🔗 Apply: http://celtics.com/jobs/data-analyst", formatted_email)

    @patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        """Test email sending with mocked SMTP server"""
        # Set up the mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Call the method
        self.email_sender.send_email(
            recipient="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        # Verify SMTP was called correctly
        mock_smtp.assert_called_once_with(self.config.smtp_server, self.config.smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(self.config.email_sender, self.config.email_password)
        self.assertTrue(mock_server.send_message.called)

    @patch.object(EmailSender, 'send_email')
    def test_send_job_listings_email(self, mock_send_email):
        """Test job listings email"""
        # Call the method
        self.email_sender.send_job_listings_email(self.sample_jobs)
        
        # Verify send_email was called with correct args
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        
        # Check recipient
        self.assertEqual(args[0], self.config.email_recipient)
        
        # Check subject contains job count
        self.assertIn("3 Jobs Found", args[1])
        
        # Check body contains team names
        self.assertIn("LAKERS", args[2])
        self.assertIn("CELTICS", args[2])

    @patch.object(EmailSender, 'send_email')
    def test_send_no_jobs_notification(self, mock_send_email):
        """Test no jobs notification email"""
        # Call the method
        self.email_sender.send_no_jobs_notification()
        
        # Verify send_email was called with correct args
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        
        # Check recipient
        self.assertEqual(args[0], self.config.email_recipient)
        
        # Check subject
        self.assertIn("No Jobs Found", args[1])
        
        # Check body contains expected message
        self.assertIn("No job openings matching your keywords were found", args[2])

    @patch.object(EmailSender, 'send_email')
    def test_send_error_notification(self, mock_send_email):
        """Test error notification email"""
        # Call the method
        error_msg = "Test error message"
        self.email_sender.send_error_notification(error_msg)
        
        # Verify send_email was called with correct args
        mock_send_email.assert_called_once()
        args = mock_send_email.call_args[0]
        
        # Check recipient
        self.assertEqual(args[0], self.config.email_recipient)
        
        # Check subject
        self.assertIn("Error", args[1])
        
        # Check body contains error message
        self.assertIn(error_msg, args[2])

if __name__ == '__main__':
    unittest.main()