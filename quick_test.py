#!/usr/bin/env python3
"""
Quick test script for NBA Career Scraper - Tests just a few teams
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper import NBAScraper
from datetime import datetime

def quick_test():
    """Test the scraper with just 3-5 teams for verification"""
    print("============================================================")
    print("NBA Career Scraper - Quick Test")
    print("============================================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize scraper
    scraper = NBAScraper()
    print(f"Keywords: {', '.join(scraper.keywords)}")
    print()
    
    # Test with just a few teams
    test_teams = [
        ("Atlanta Hawks", "https://wd1.myworkdaysite.com/en-US/recruiting/hawks/External"),
        ("Charlotte Hornets", "https://recruiting.ultipro.com/HOR1011HORNT/JobBoard/5b257d2d-0813-4167-b64c-95fb001e0d96/?q=&o=postedDateDesc"),
        ("Cleveland Cavaliers", "https://www.teamworkonline.com/basketball-jobs/cleveland-cavaliers"),
        ("Dallas Mavericks", "https://mavs.wd1.myworkdaysite.com/en-US/recruiting/mavs/External"),
        ("Denver Nuggets", "https://kroenke-sports-entertainment.jobs.net/en-GB/search/?createNewAlert=false&q=&locationsearch=&geolocation=")
    ]
    
    total_jobs = 0
    total_teams = len(test_teams)
    start_time = datetime.now()
    
    print("Testing scraper with 5 representative teams...")
    print("This should take about 1-2 minutes...")
    print()
    
    for team_name, url in test_teams:
        print(f"Testing {team_name}...")
        team_start = datetime.now()
        
        try:
            jobs = scraper._fetch_jobs_from_team_page(team_name, url)
            team_time = (datetime.now() - team_start).total_seconds()
            
            if jobs:
                print(f"✅ {team_name}: {len(jobs)} jobs found ({team_time:.1f}s)")
                total_jobs += len(jobs)
                # Show first few job titles as examples
                for i, job in enumerate(jobs[:3]):
                    print(f"   • {job['title']}")
                if len(jobs) > 3:
                    print(f"   ... and {len(jobs) - 3} more")
            else:
                print(f"⚠️  {team_name}: No jobs found ({team_time:.1f}s)")
                
        except Exception as e:
            team_time = (datetime.now() - team_start).total_seconds()
            print(f"❌ {team_name}: Error - {str(e)} ({team_time:.1f}s)")
        
        print()
    
    # Summary
    total_time = (datetime.now() - start_time).total_seconds()
    avg_time = total_time / total_teams
    
    print("============================================================")
    print("QUICK TEST SUMMARY")
    print("============================================================")
    print(f"Total jobs found: {total_jobs}")
    print(f"Teams tested: {total_teams}")
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Average time per team: {avg_time:.1f} seconds")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if total_jobs > 20:
        print("✅ Test PASSED - Good job coverage found!")
    elif total_jobs > 10:
        print("⚠️  Test PARTIAL - Some jobs found, system working")
    else:
        print("❌ Test FAILED - Very few jobs found, check system")
    
    # Cleanup
    scraper.close()

if __name__ == "__main__":
    quick_test()
