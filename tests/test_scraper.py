#!/usr/bin/env python3
"""
Simple test script to verify the NBA career scraper is working correctly.
This runs without requiring email configuration.
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.scraper import JobScraper
from src.config import Config

def main():
    print("=" * 60)
    print("NBA Career Scraper - Test Run")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load keywords
    config = Config()
    kw_data = config.load_keywords()
    keywords = kw_data.get('keywords', [])
    exclude = kw_data.get('exclude', [])
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Excluded keywords: {', '.join(exclude)}")

    # Initialize scraper
    print("\nInitializing scraper...")
    scraper = JobScraper(keywords=keywords, exclude=exclude)

    # Test loading team URLs
    scraper.load_team_urls()
    print(f"Loaded {len(scraper.team_urls)} team URLs")
    
    # Run the scraper
    print("\nStarting job scraping across all NBA teams...")
    print("This may take a few minutes...")
    
    all_jobs = scraper.scrape_all_teams()
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if all_jobs:
        total_jobs = sum(len(jobs) for jobs in all_jobs.values())
        print(f"Teams with job openings: {len(all_jobs)}")
        print(f"Total jobs found: {total_jobs}")
        
        print("\nJobs by team:")
        for team_name, jobs in sorted(all_jobs.items()):
            print(f"  {team_name}: {len(jobs)} jobs")
        
        # Show job listings
        print("\nJob listings:")
        for team_name, jobs in all_jobs.items():
            for job in jobs:  # Jobs for each team
                print(f"  • {team_name}: {job['title']}")
                print(f"    {job['url']}")
            print()  # Newline between teams for readability
        
        # Keyword analysis
        print("\nKeyword matches:")
        keyword_counts = {}
        for team_name, jobs in all_jobs.items():
            for job in jobs:
                title_lower = job['title'].lower()
                for keyword in keywords:
                    if keyword.lower() in title_lower:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {keyword}: {count}")
        
        print(f"\n✅ Success! Found {total_jobs} job opportunities across {len(all_jobs)} NBA teams.")
        print("The scraper is working correctly and ready for production use.")
        
    else:
        print("❌ No jobs found. This could mean:")
        print("  - No current openings match your keywords")
        print("  - Some team websites are experiencing issues")
        print("  - The scraper selectors may need updating")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
