import time
import logging
from scraper import JobScraper
from email_sender import EmailSender
from config import Config

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraper.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting NBA Career Scraper")
    
    try:
        # Load configuration
        config = Config()
        kw_data = config.load_keywords()
        keywords = kw_data.get('keywords', [])
        exclude = kw_data.get('exclude', [])
        
        # Initialize scraper
        job_scraper = JobScraper(keywords=keywords, exclude=exclude)
        
        # Initialize email sender
        email_sender = EmailSender(config)
        
        # Scrape jobs from all teams using curated URLs
        logger.info("Starting job scraping from curated team URLs...")
        all_jobs = job_scraper.scrape_all_teams()
        
        if all_jobs:
            # Flatten the jobs for email sending
            job_listings = []
            for team_name, jobs in all_jobs.items():
                job_listings.extend(jobs)
            
            logger.info(f"Found {len(job_listings)} total matching job listings across {len(all_jobs)} teams")
            
            # Send email with results
            try:
                email_sender.send_job_listings_email(all_jobs)  # Pass the organized structure
                logger.info("Email sent successfully")
            except Exception as e:
                logger.error(f"Error sending email: {e}")
        else:
            logger.info("No matching job listings found")
            
            # Send notification that no jobs were found
            try:
                email_sender.send_no_jobs_notification()
                logger.info("No jobs notification sent")
            except Exception as e:
                logger.error(f"Error sending no jobs notification: {e}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

def run_periodic_check(interval_hours=24):
    """Run the scraper periodically"""
    logger = logging.getLogger(__name__)
    
    while True:
        try:
            main()
            logger.info(f"Sleeping for {interval_hours} hours...")
            time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            logger.info("Scraper stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in periodic check: {e}")
            logger.info("Continuing with next check...")
            time.sleep(3600)  # Wait 1 hour before retrying

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--periodic":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        run_periodic_check(hours)
    else:
        main()