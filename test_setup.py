#!/usr/bin/env python3
"""
Test script to verify the NBA Career Scraper setup and functionality.
Run this script to test the scraper without sending emails.
"""

import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import JobScraper
from config import Config
from utils import setup_logging, ensure_directories_exist

def test_scraper():
    """Test the basic scraper functionality"""
    print("🏀 NBA Career Scraper Test")
    print("=" * 50)
    
    # Set up logging
    setup_logging()
    ensure_directories_exist()
    
    # Load keywords
    try:
        with open('../data/keywords.json', 'r') as f:
            keywords_data = json.load(f)
            keywords = keywords_data.get('keywords', [])
        print(f"✅ Loaded {len(keywords)} keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
    except Exception as e:
        print(f"❌ Error loading keywords: {e}")
        keywords = ['analytics', 'data', 'marketing']  # Fallback keywords
        print(f"Using fallback keywords: {keywords}")
    
    # Initialize scraper
    scraper = JobScraper(keywords=keywords)
    
    # Test team URL discovery
    print("\n🔍 Testing team URL discovery...")
    try:
        team_urls = scraper.fetch_team_urls_from_nba_careers()
        if team_urls:
            print(f"✅ Found {len(team_urls)} team career pages")
            for i, (team, url) in enumerate(list(team_urls.items())[:3]):
                print(f"   {i+1}. {team}: {url}")
            if len(team_urls) > 3:
                print(f"   ... and {len(team_urls) - 3} more teams")
        else:
            print("❌ No team URLs found")
            return False
    except Exception as e:
        print(f"❌ Error discovering team URLs: {e}")
        return False
    
    # Test scraping a single team (limit to avoid being too aggressive)
    print("\n🕷️  Testing job scraping for one team...")
    try:
        test_team = list(team_urls.items())[0]  # Get first team
        team_name, team_url = test_team
        print(f"Testing with: {team_name}")
        
        jobs = scraper._fetch_jobs_from_team_page(team_name, team_url)
        
        if jobs:
            print(f"✅ Found {len(jobs)} jobs for {team_name}")
            for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                print(f"   {i+1}. {job['title']}")
                if job.get('location'):
                    print(f"      Location: {job['location']}")
                print(f"      URL: {job['url']}")
        else:
            print(f"ℹ️  No jobs found for {team_name} (may be normal)")
            
    except Exception as e:
        print(f"❌ Error testing job scraping: {e}")
        return False
    
    # Test keyword filtering
    print("\n🔍 Testing keyword filtering...")
    if jobs:
        filtered_jobs = scraper.filter_jobs_by_keywords(jobs)
        print(f"✅ Filtered to {len(filtered_jobs)} jobs matching keywords")
        
        for job in filtered_jobs[:2]:  # Show first 2 filtered jobs
            matching_keywords = [kw for kw in keywords 
                               if kw.lower() in job['title'].lower() or 
                                  kw.lower() in job['description'].lower()]
            print(f"   - {job['title']} (matches: {', '.join(matching_keywords)})")
    else:
        print("ℹ️  No jobs to filter")
    
    print("\n✅ Test completed successfully!")
    print("\nTo run the full scraper:")
    print("  python src/main.py")
    print("\nTo run periodically:")
    print("  python src/main.py --periodic 24")
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        config = Config()
        
        # Check if email is configured
        if config.email_sender and config.email_password:
            print("✅ Email configuration found")
        else:
            print("⚠️  Email not configured (set up .env file for email notifications)")
            
        print(f"   SMTP Server: {config.smtp_server}:{config.smtp_port}")
        print(f"   Check Interval: {config.check_interval_hours} hours")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    print("Starting NBA Career Scraper tests...\n")
    
    # Test configuration
    config_ok = test_config()
    
    # Test scraper functionality  
    scraper_ok = test_scraper()
    
    if config_ok and scraper_ok:
        print("\n🎉 All tests passed! The scraper is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
