import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from urllib.parse import urljoin, urlparse
import json

class JobScraper:
    def __init__(self, keywords=None):
        self.keywords = keywords or []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.team_urls = {}
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _fetch_jobs_from_team_page(self, team_name, url):
        """
        Fetch job listings from a specific team's career page
        """
        jobs = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple strategies to find job listings
            job_elements = self._find_job_elements(soup)
            
            for job_element in job_elements:
                job_data = self._parse_job_element(job_element, team_name, url)
                if job_data:
                    jobs.append(job_data)
            
            # Handle pagination if present
            next_page_url = self._find_next_page(soup, url)
            if next_page_url:
                jobs.extend(self._fetch_jobs_from_team_page(team_name, next_page_url))
                
        except Exception as e:
            self.logger.error(f"Error fetching jobs from {url}: {e}")
            
        return jobs

    def _find_job_elements(self, soup):
        """
        Enhanced job element finder that handles multiple career site formats.
        Each team uses different platforms, so we need comprehensive selectors.
        """
        job_elements = []
        
        # Comprehensive selectors for different platforms
        selectors = [
            # Workday sites (myworkdaysite.com)
            'a[data-automation-id="jobTitle"]',  # Primary Workday job titles
            'a[href*="/job/"]',  # Workday job URLs
            
            # UltiPro sites (recruiting.ultipro.com)
            'a[href*="JobDetails"]',  # UltiPro job detail links
            '.job-link',  # UltiPro job links
            '.job-title a',  # UltiPro job titles
            '.posting-headline a',  # UltiPro posting headlines
            
            # TeamWork Online
            '.list-group-item a',  # TeamWork job list items
            '.job-title-link',  # TeamWork job title links
            'a[href*="/job/"]',  # TeamWork job URLs
            
            # ADP Workforce Now
            'a[href*="jobdetails"]',  # ADP job detail links
            '.job-result-item a',  # ADP job results
            
            # Dayforce HCM
            'a[href*="JobDetail"]',  # Dayforce job details
            '.job-item a',  # Dayforce job items
            
            # ICIMS (careers-grizzlies.icims.com)
            'a[href*="jobs/"]',  # ICIMS job URLs
            '.iCIMS_JobsTable a',  # ICIMS job table
            
            # SmartRecruiters (careers.smartrecruiters.com)
            'a[href*="/jobs/"]',  # SmartRecruiters job URLs
            '.job-link',  # SmartRecruiters job links
            
            # Paylocity
            'a[href*="recruiting/jobs"]',  # Paylocity job URLs
            
            # Paycor
            'a[href*="JobDetail"]',  # Paycor job details
            
            # HireBridge
            'a[href*="JobDetails"]',  # HireBridge job details
            
            # Custom NBA sites and general patterns
            'a[href*="job"]',  # Generic job URLs
            'a[href*="career"]',  # Generic career URLs
            'a[href*="position"]',  # Generic position URLs
            'a[href*="opening"]',  # Generic opening URLs
            
            # Title-based selectors
            'a[title*="job" i]',  # Job in title
            'a[title*="position" i]',  # Position in title
            'a[title*="career" i]',  # Career in title
            'a[title*="opening" i]',  # Opening in title
            
            # Class-based selectors
            '.job a',  # Job class links
            '.position a',  # Position class links
            '.career a',  # Career class links
            '.opening a',  # Opening class links
            '.job-listing a',  # Job listing links
            '.job-item a',  # Job item links
            '.career-opportunity a',  # Career opportunity links
            
            # Fallback selectors for unusual layouts
            'a[aria-label*="job" i]',  # ARIA label with job
            'a[aria-label*="position" i]',  # ARIA label with position
        ]
        
        # Try each selector and collect results
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    self.logger.info(f"Found {len(elements)} job elements using selector: {selector}")
                    job_elements.extend(elements)
            except Exception as e:
                self.logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Remove duplicates while preserving order
        seen_hrefs = set()
        unique_elements = []
        for element in job_elements:
            href = element.get('href', '')
            # Use both href and text to identify unique jobs
            identifier = f"{href}|{element.get_text(strip=True)[:50]}"
            if identifier not in seen_hrefs:
                seen_hrefs.add(identifier)
                unique_elements.append(element)
        
        # If we still don't have jobs, try text-based detection
        if not unique_elements:
            self.logger.info("No jobs found with standard selectors, trying text-based detection...")
            links = soup.find_all('a', href=True)
            for link in links:
                text = link.get_text(strip=True).lower()
                href = link.get('href', '').lower()
                
                # Job title indicators
                job_indicators = [
                    "analytics",
                    "data",
                    "basketball",
                    "strategy",
                    "software",
                    "engineer",
                    "developer",
                    "full stack",
                    "front end"
                ]
                
                if (any(indicator in text for indicator in job_indicators) or 
                    any(keyword in href for keyword in ['job', 'career', 'position', 'opening'])):
                    if len(text) > 3:  # Skip very short links
                        unique_elements.append(link)
        
        self.logger.info(f"Found {len(unique_elements)} total unique job elements")
        return unique_elements

    def _parse_job_element(self, element, team_name, base_url):
        """
        Enhanced job element parsing for different platforms
        """
        try:
            # Strategy 1: Try to find title in various tag types
            title_element = None
            title_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', '.title', '.job-title', '.position-title']
            
            for selector in title_selectors:
                title_element = element.find(selector)
                if title_element:
                    break
            
            # If no title element found, use the element's own text
            if title_element:
                title = title_element.get_text(strip=True)
            else:
                title = element.get_text(strip=True)
            
            # Clean up title
            title = self._clean_title(title)
            
            # Strategy 2: Find job link
            job_url = base_url  # Default fallback
            
            # Look for href in the element itself
            if element.name == 'a' and element.get('href'):
                job_url = urljoin(base_url, element.get('href'))
            else:
                # Look for a link within the element
                link_element = element.find('a', href=True)
                if link_element:
                    job_url = urljoin(base_url, link_element.get('href'))
            
            # Only return valid jobs (with meaningful titles)
            if not self._is_valid_job_title(title):
                return None
            
            return {
                'title': title,
                'team': team_name,
                'url': job_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing job element: {e}")
            return None

    def _clean_title(self, title):
        """
        Clean and normalize job titles
        """
        if not title:
            return "Unknown Position"
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['job:', 'position:', 'opening:', 'career:']
        suffixes_to_remove = ['- apply now', '(apply)', 'apply']
        
        title_lower = title.lower()
        for prefix in prefixes_to_remove:
            if title_lower.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        for suffix in suffixes_to_remove:
            if title_lower.endswith(suffix):
                title = title[:-len(suffix)].strip()
                break
        
        return title

    def _is_valid_job_title(self, title):
        """
        Check if a title represents a real job posting (not navigation or general links)
        """
        if not title or len(title) < 3:
            return False
        
        title_lower = title.lower().strip()
        
        # Invalid titles - navigation, technical, or generic links
        invalid_titles = {
            'home', 'careers', 'jobs', 'search', 'apply', 'login', 'register',
            'about', 'contact', 'privacy', 'terms', 'help', 'support',
            'download chrome', 'google chrome', 'update browser', 'browser',
            'who we are', 'our company', 'company', 'mission', 'vision',
            'benefits', 'culture', 'diversity', 'inclusion',
            'more info', 'learn more', 'view all', 'see all', 'show more',
            'apply now', 'submit application', 'submit resume',
            'back to jobs', 'return to search', 'job search',
            'filter', 'sort', 'clear', 'reset',
            'loading', 'please wait', 'error', 'not found',
            'share', 'print', 'email', 'save',
            'previous', 'next', 'page', 'results',
            'privacy policy', 'cookie policy', 'terms of service',
            'accessibility', 'equal opportunity'
        }
        
        # Check exact matches
        if title_lower in invalid_titles:
            return False
        
        # Check if it starts with common navigation patterns
        invalid_prefixes = [
            'view', 'see', 'show', 'click', 'go to', 'navigate',
            'download', 'install', 'update', 'upgrade'
        ]
        
        for prefix in invalid_prefixes:
            if title_lower.startswith(prefix + ' '):
                return False
        
        # Must contain job-related words or be reasonably long
        job_indicators = [
            'manager', 'director', 'coordinator', 'analyst', 'specialist',
            'assistant', 'associate', 'intern', 'executive', 'lead',
            'supervisor', 'administrator', 'officer', 'representative',
            'developer', 'engineer', 'designer', 'architect', 'consultant',
            'sales', 'marketing', 'finance', 'accounting', 'hr', 'legal',
            'operations', 'coach', 'scout', 'trainer', 'nutritionist',
            'physician', 'therapist', 'security', 'maintenance', 'custodial',
            'ticket', 'event', 'guest', 'customer', 'client', 'fan',
            'media', 'broadcast', 'video', 'audio', 'graphic', 'content',
            'data', 'research', 'analytics', 'business', 'strategy',
            'project', 'program', 'product', 'service', 'support'
        ]
        
        # If title is short, it must contain job indicators
        if len(title_lower) < 20:
            return any(indicator in title_lower for indicator in job_indicators)
        
        # Longer titles are more likely to be valid job titles
        return True
    
    def _find_next_page(self, soup, current_url):
        """
        Find next page URL for pagination
        """
        next_links = soup.find_all('a', href=True)
        
        for link in next_links:
            text = link.get_text(strip=True).lower()
            if any(keyword in text for keyword in ['next', 'more', '→', '>']):
                return urljoin(current_url, link.get('href'))
        
        return None

    def filter_jobs_by_keywords(self, job_listings):
        """
        Filter job listings based on keywords
        """
        if not self.keywords:
            return job_listings
            
        filtered_jobs = []
        
        for job in job_listings:
            title_lower = job['title'].lower()
            description_lower = job['description'].lower()
            
            # Check if any keyword matches title or description
            if any(keyword.lower() in title_lower or keyword.lower() in description_lower 
                   for keyword in self.keywords):
                filtered_jobs.append(job)
                
        self.logger.info(f"Filtered {len(filtered_jobs)} jobs from {len(job_listings)} total jobs")
        return filtered_jobs

    def save_team_urls(self, filename='data/team_urls.json'):
        """
        Save discovered team URLs to JSON file
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.team_urls, f, indent=2)
            self.logger.info(f"Saved team URLs to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving team URLs: {e}")

    def load_team_urls(self, filename='data/team_urls.json'):
        """
        Load team URLs from JSON file
        """
        try:
            with open(filename, 'r') as f:
                self.team_urls = json.load(f)
            self.logger.info(f"Loaded {len(self.team_urls)} team URLs from {filename}")
        except Exception as e:
            self.logger.error(f"Error loading team URLs: {e}")
            self.team_urls = {}

    def scrape_all_teams(self):
        """
        Scrape job listings from all teams using the curated URLs.
        Returns a dictionary of jobs organized by team.
        """
        all_jobs = {}
        
        # Load the curated team URLs
        self.load_team_urls()
        
        if not self.team_urls:
            self.logger.error("No team URLs loaded. Please check data/team_urls.json")
            return all_jobs
        
        self.logger.info(f"Starting to scrape {len(self.team_urls)} team career pages...")
        
        for team_name, url in self.team_urls.items():
            self.logger.info(f"\n--- Scraping {team_name} ---")
            self.logger.info(f"URL: {url}")
            
            try:
                # Scrape jobs for this team
                jobs = self._fetch_jobs_from_team_page(team_name, url)
                
                if jobs:
                    all_jobs[team_name] = jobs
                    self.logger.info(f"Found {len(jobs)} jobs for {team_name}")
                else:
                    self.logger.info(f"No jobs found for {team_name}")
                
                # Small delay between requests to be respectful
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error scraping {team_name}: {e}")
                continue
        
        total_jobs = sum(len(jobs) for jobs in all_jobs.values())
        self.logger.info("\n=== Scraping Complete ===")
        self.logger.info(f"Total teams with jobs: {len(all_jobs)}")
        self.logger.info(f"Total jobs found: {total_jobs}")
        
        return all_jobs