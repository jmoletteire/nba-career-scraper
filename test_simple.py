#!/usr/bin/env python3
"""
Simple test runner for the NBA Career Scraper
This version doesn't require email configuration and just prints results.
"""

import sys
import os
import json
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import JobScraper

def main():
    print("🏀 NBA Career Scraper - Test Mode")
    print("=" * 50)
    
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Load keywords
    try:
        with open('data/keywords.json', 'r') as f:
            keywords_data = json.load(f)
            keywords = keywords_data.get('keywords', [])
        print(f"✅ Loaded {len(keywords)} keywords")
    except Exception as e:
        print(f"❌ Error loading keywords: {e}")
        return
    
    # Initialize scraper
    scraper = JobScraper(keywords=keywords)
    
    # Test team URL discovery
    print("\n🔍 Discovering NBA team career pages...")
    team_urls = scraper.fetch_team_urls_from_nba_careers()
    
    if not team_urls:
        print("❌ No team URLs found. Checking manually...")
        # Try to load from existing file
        try:
            scraper.load_team_urls()
            team_urls = scraper.team_urls
            print(f"✅ Loaded {len(team_urls)} team URLs from file")
        except Exception:
            print("❌ Could not load team URLs")
            return
    
    # Test scraping from a few teams (limit to 3 for testing)
    print("\n🕷️  Testing job scraping from first 3 teams...")
    test_teams = list(team_urls.items())[:3]
    
    all_jobs = []
    for team_name, team_url in test_teams:
        print(f"\nScraping {team_name}...")
        try:
            jobs = scraper._fetch_jobs_from_team_page(team_name, team_url)
            if jobs:
                print(f"  ✅ Found {len(jobs)} jobs")
                all_jobs.extend(jobs)
            else:
                print("  ℹ️  No jobs found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test keyword filtering
    if all_jobs:
        print(f"\n🔍 Filtering {len(all_jobs)} jobs by keywords...")
        filtered_jobs = scraper.filter_jobs_by_keywords(all_jobs)
        
        print(f"✅ Found {len(filtered_jobs)} matching jobs:")
        for i, job in enumerate(filtered_jobs[:5]):  # Show first 5
            print(f"\n{i+1}. {job['title']}")
            print(f"   Team: {job['team']}")
            if job.get('location'):
                print(f"   Location: {job['location']}")
            print(f"   URL: {job['url']}")
            if job.get('description'):
                print(f"   Description: {job['description'][:100]}...")
    else:
        print("\nℹ️  No jobs found to filter")
    
    print("\n✅ Test completed!")
    print("\nTo run with email notifications:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your email credentials") 
    print("3. Run: python src/main.py")

if __name__ == "__main__":
    main()
