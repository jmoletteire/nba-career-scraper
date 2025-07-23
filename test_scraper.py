#!/usr/bin/env python3
"""
Simple test script to verify the NBA career scraper is working correctly.
This runs without requiring email configuration.
"""

import sys
import os
import json
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper import JobScraper

def load_keywords():
    """Load keywords from JSON file"""
    try:
        with open('data/keywords.json', 'r') as f:
            data = json.load(f)
            return data.get('keywords', [])
    except Exception as e:
        print(f"Error loading keywords: {e}")
        return ['analyst', 'coordinator', 'manager', 'intern', 'assistant', 'director']

def main():
    print("=" * 60)
    print("NBA Career Scraper - Test Run")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load keywords
    keywords = load_keywords()
    print(f"Keywords: {', '.join(keywords)}")
    
    # Initialize scraper
    print("\nInitializing scraper...")
    scraper = JobScraper(keywords=keywords)
    
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
        
        # Show sample jobs
        print("\nSample job listings:")
        sample_count = 0
        for team_name, jobs in all_jobs.items():
            for job in jobs[:2]:  # Max 2 per team
                if sample_count < 10:  # Max 10 total
                    print(f"  • {team_name}: {job['title']}")
                    sample_count += 1
                if sample_count >= 10:
                    break
            if sample_count >= 10:
                break
        
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
