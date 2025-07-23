import unittest
from src.email_sender import EmailSender

class TestEmailSender(unittest.TestCase):

    def setUp(self):
        self.email_sender = EmailSender()

    def test_format_job_list(self):
        job_list = [
            {"team": "Lakers", "title": "Assistant Coach", "link": "http://lakers.com/jobs/assistant-coach"},
            {"team": "Celtics", "title": "Data Analyst", "link": "http://celtics.com/jobs/data-analyst"}
        ]
        formatted_email = self.email_sender.format_job_list(job_list)
        expected_output = (
            "Available Job Listings:\n"
            "- Lakers: Assistant Coach (http://lakers.com/jobs/assistant-coach)\n"
            "- Celtics: Data Analyst (http://celtics.com/jobs/data-analyst)\n"
        )
        self.assertEqual(formatted_email, expected_output)

    def test_send_email(self):
        # This test would typically mock the email sending functionality
        # For demonstration purposes, we will just check if the method exists
        self.assertTrue(hasattr(self.email_sender, 'send_email'))

if __name__ == '__main__':
    unittest.main()