import unittest
from src.scraper import JobScraper

class TestJobScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = JobScraper()

    def test_fetch_team_jobs(self):
        # Test fetching jobs from a sample team URL
        team_url = "https://www.nba.com/team/careers"
        jobs = self.scraper.fetch_team_jobs(team_url)
        self.assertIsInstance(jobs, list)

    def test_parse_job_listing(self):
        # Test parsing a sample job listing
        sample_listing = {
            'title': 'Data Analyst',
            'link': 'https://www.nba.com/team/careers/data-analyst',
            'team': 'Sample Team'
        }
        parsed_job = self.scraper.parse_job_listing(sample_listing)
        self.assertIn('title', parsed_job)
        self.assertIn('link', parsed_job)
        self.assertIn('team', parsed_job)

if __name__ == '__main__':
    unittest.main()