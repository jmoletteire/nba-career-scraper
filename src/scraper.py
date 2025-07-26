from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class JobScraper:
    def __init__(self, keywords=None, exclude=None, use_selenium=True):
        self.keywords = keywords or []
        self.exclude = exclude or []
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.team_urls = {}
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Selenium driver if needed
        self.driver = None
        if self.use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with Chrome options - optimized for speed"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            # Speed optimizations
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--mute-audio')
            chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # Disable images
            chrome_options.add_argument('--disable-animations')
            chrome_options.add_argument('--window-size=1280,720')  # Smaller window
            
            prefs = {
                'profile.default_content_setting_values': {
                    'images': 2,        # Block images
                    'plugins': 2,       # Block plugins
                    'geolocation': 2,   # Block geolocation
                    'notifications': 2  # Block notifications
                }
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(5)  # Reduce from 10 to 5 seconds
            self.logger.info("Selenium WebDriver initialized with speed optimizations")
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
            self.driver = None
    
    def __del__(self):
        """Cleanup Selenium driver when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

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
        if not title:
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
        
        # Check if it contains any keywords and not any exclude terms
        return any(indicator in title_lower for indicator in self.keywords) and not any(indicator in title_lower for indicator in self.exclude)
    
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
        
    def _find_job_elements(self, soup):
        """
        Enhanced job element finder that handles multiple career site formats.
        Each team uses different platforms, so we need comprehensive selectors.
        """
        job_elements = []
        
        # Comprehensive selectors for different platforms
        selectors = [
            # Workday sites (Atlanta)
            'a[data-automation-id="jobTitle"]',
            
            # UltiPro sites (Charlotte, Miami, Orlando, Phoenix)
            'a[data-automation="job-title"]',
            
            # TeamWork Online (Cleveland, GS, LAL, Sacramento, Utah, Washington)
            'a[href*="/basketball-jobs/"]',
            
            # Paylocity (Detroit)
            'a[href*="Recruiting/Jobs"]',
            
            # Paycor (Chicago, Dallas, Denver, Houston)
            'a[href*="JobIntroduction"]',  # Paycor job details
            
            # HireBridge (Philly)
            'a[href*="jobloc"]',
            
            # Generic job URLs
            'a[href*="/jobs/"]',  # Memphis, Minnesota, NOLA, New York, Portland, San Antonio
            'a[href*="linkedin"]',  # Boston
            'a[href*="job-opening"]',  # Indiana
            'a[href*="/clippers/company/careers/"]',  # LAC
            'a[href*="/thunder/employment/"]',  # OKC
            'a[href*="/MLSE3/"]',  # Toronto
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
                
                # Check if it matches any keywords
                if (any(indicator in text for indicator in self.keywords)):
                    if len(text) > 3:  # Skip very short links
                        unique_elements.append(link)
        
        self.logger.info(f"Found {len(unique_elements)} total unique job elements")
        return unique_elements

    def _parse_job_element_selenium(self, element, team_name, base_url):
        """
        Parse job element using Selenium WebElement
        """
        try:
            # Get title
            title = element.text.strip() if element.text else "Unknown Position"
            
            # Get URL
            job_url = element.get_attribute('href') or base_url
            
            # Clean up title
            title = self._clean_title(title)
            
            # Validate job title
            if not self._is_valid_job_title(title):
                return None
            
            return {
                'title': title,
                'team': team_name,
                'url': job_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing Selenium job element: {e}")
            return None

    def _find_job_elements_selenium(self, team_name):
        """
        Find job elements using Selenium - optimized for speed
        """
        job_elements = []
        
        # Prioritized selectors - most effective first, stop when we find jobs
        priority_selectors = {
            # Platform-specific high-yield selectors
            # Workday sites (Atlanta)
            'Atlanta Hawks': 'a[data-automation-id="jobTitle"]',
            
            # UltiPro sites (Charlotte, Miami, Orlando, Phoenix)
            'Charlotte Hornets': 'a[data-automation="job-title"]',
            'Miami Heat': 'a[data-automation="job-title"]',
            'Orlando Magic': 'a[data-automation="job-title"]',
            'Phoenix Suns': 'a[data-automation="job-title"]',
            
            # TeamWork Online (Cleveland, GS, LAL, Sacramento, Utah, Washington)
            'Cleveland Cavaliers': 'a[href*="/basketball-jobs/"]',
            'Golden State Warriors': 'a[href*="/basketball-jobs/"]',
            'Los Angeles Lakers': 'a[href*="/basketball-jobs/"]',
            'Sacramento Kings': 'a[href*="/basketball-jobs/"]',
            'Utah Jazz': 'a[href*="/basketball-jobs/"]',
            'Washington Wizards': 'a[href*="/basketball-jobs/"]',

            # Paylocity (Detroit)
            'Detroit Pistons': 'a[href*="Recruiting/Jobs"]',

            # Paycor (Chicago, Dallas, Denver, Houston)
            'Chicago Bulls': 'a[href*="JobIntroduction"]',
            'Dallas Mavericks': 'a[href*="JobIntroduction"]',
            'Denver Nuggets': 'a[href*="JobIntroduction"]',
            'Houston Rockets': 'a[href*="JobIntroduction"]',

            # HireBridge (Philly)
            'Philadelphia 76ers': 'a[href*="jobloc"]',

            # Misc. job URLs
            'Memphis Grizzlies': 'a[href*="/jobs/"]',
            'Minnesota Timberwolves': 'a[href*="/jobs/"]',
            'New Orleans Pelicans': 'a[href*="/jobs/"]',
            'New York Knicks': 'a[href*="/jobs/"]',
            'Portland Trail Blazers': 'a[href*="/jobs/"]',
            'San Antonio Spurs': 'a[href*="/jobs/"]',
            'Boston Celtics': 'a[href*="linkedin"]',
            'Indiana Pacers': 'a[href*="job-opening"]',
            'Los Angeles Clippers': 'a[href*="/clippers/company/careers/"]',
            'Oklahoma City Thunder': 'a[href*="/thunder/employment/"]',
            'Toronto Raptors': 'a[href*="/MLSE3/"]',
        }
        
        try:
            # Search page once with combined selector
            self.logger.info("Searching...")
            elements = self.driver.find_elements(By.CSS_SELECTOR, priority_selectors.get(team_name, 'a[href*="job"]'))
            
            if elements:
                self.logger.info(f"Found {len(elements)} job elements")
                job_elements.extend(elements)
                
        except Exception as e:
            self.logger.error(f"Selector search failed: {e}")
        
        return job_elements

    def _fetch_jobs_with_requests(self, team_name, url):
        """
        Fetch jobs using requests + BeautifulSoup for static sites
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
                    
        except Exception as e:
            self.logger.error(f"Error fetching jobs with requests from {url}: {e}")
            
        return jobs
    
    def _fetch_jobs_with_selenium(self, team_name, url):
        """
        Fetch jobs using Selenium for JavaScript-heavy sites - optimized for speed
        """
        jobs = []
        
        if not self.driver:
            self.logger.warning(f"Selenium not available for {team_name}, falling back to requests")
            return self._fetch_jobs_with_requests(team_name, url)
        
        try:
            self.logger.info(f"Using Selenium to load {url}")
            self.driver.get(url)
            
            # Remove the explicit wait - we already have implicit wait set
            # Reduce fixed sleep time from 2 seconds to 0.5 seconds
            time.sleep(0.5)
            
            # Try to find job elements using Selenium
            job_elements = self._find_job_elements_selenium(team_name)
            
            seen_hrefs = set()
            for job_element in job_elements:
                try:
                    href = job_element.get_attribute('href') or ''
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        job_data = self._parse_job_element_selenium(job_element, team_name, url)
                        if job_data:
                            jobs.append(job_data)
                    else:
                        continue
                except Exception:
                    continue
                
        except Exception as e:
            self.logger.error(f"Error fetching jobs with Selenium from {url}: {e}")
            
        return jobs
     
    def _should_use_selenium(self):
        """
        Determine if we should use Selenium - always use it if available
        """
        # Always use Selenium if available for consistent results across all sites
        return self.use_selenium and self.driver is not None
    
    def _fetch_jobs_from_team_page(self, team_name, url):
        """
        Fetch job listings from a specific team's career page using Selenium or requests
        """
        jobs = []
        
        # Determine which method to use based on the URL
        if self._should_use_selenium():
            jobs = self._fetch_jobs_with_selenium(team_name, url)
        else:
            jobs = self._fetch_jobs_with_requests(team_name, url)
            
        return jobs

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
                    self.logger.info(f"Found {len(jobs)} matching jobs for {team_name}")
                else:
                    self.logger.info(f"No matching jobs found for {team_name}")
                
            except Exception as e:
                self.logger.error(f"Error scraping {team_name}: {e}")
                continue
        
        total_jobs = sum(len(jobs) for jobs in all_jobs.values())
        self.logger.info("\n=== Scraping Complete ===")
        self.logger.info(f"Total teams with jobs: {len(all_jobs)}")
        self.logger.info(f"Total jobs found: {total_jobs}")
        
        return all_jobs
