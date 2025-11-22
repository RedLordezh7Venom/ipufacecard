import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from typing import Optional, Tuple, List

# Global scraper instance for simple function calls
_global_scraper = None

def extract_student_image_and_name(enrollment_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Simple function to extract student image and name.
    This is the main function to import and use in other scripts.
    
    Args:
        enrollment_id: Student enrollment/ID number
        
    Returns:
        Tuple of (image_url, name) - either can be None if unavailable
        
    Example:
        from scraper import extract_student_image_and_name
        
        image_url, name = extract_student_image_and_name("09518241723")
        if image_url:
            print(f"Got image: {image_url}")
        if name:
            print(f"Got name: {name}")
    """
    global _global_scraper
    if _global_scraper is None:
        _global_scraper = ProxyScraper(max_workers=4)
    
    return _global_scraper.extract_student_image_and_name(enrollment_id)


class ProxyScraper:
    def __init__(self, proxies: List[str] = None, max_workers: int = 5):
        """
        Initialize the scraper with optional proxies and parallel workers
        
        Args:
            proxies: List of proxy addresses (e.g., ['http://proxy1:port', 'http://proxy2:port'])
            max_workers: Number of parallel threads (default: 5)
        """
        self.proxies = proxies or []
        self.max_workers = max_workers
        
    def get_chrome_options(self, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Options:
        """Create optimized Chrome options"""
        chrome_options = Options()
        
        # Headless and performance settings
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-images')  # Don't load images (faster)
        chrome_options.add_argument('--disable-javascript')  # If JS not needed
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Memory optimization
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--single-process')
        
        # Proxy configuration
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Random user agent for better stealth
        if user_agent:
            chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Additional stealth options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        return chrome_options

    def get_random_user_agent(self) -> str:
        """Return a random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        return random.choice(user_agents)

    def extract_student_data(self, student_id: str, retry_count: int = 2) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract student image URL and name with retry logic
        
        Returns:
            Tuple of (student_id, image_url, name)
        """
        url = f"https://www.ipuranklist.com/student/{student_id}"
        proxy = random.choice(self.proxies) if self.proxies else None
        
        for attempt in range(retry_count + 1):
            driver = None
            try:
                # Setup Chrome with options
                chrome_options = self.get_chrome_options(
                    proxy=proxy,
                    user_agent=self.get_random_user_agent()
                )
                
                driver = webdriver.Chrome(options=chrome_options)
                driver.set_page_load_timeout(15)  # Timeout after 15 seconds
                
                # Navigate to URL
                driver.get(url)
                
                # Try to extract image URL (but don't fail if unavailable)
                image_url = None
                try:
                    wait = WebDriverWait(driver, 5)  # Shorter timeout for image
                    img_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='assets.ipuranklist.com']"))
                    )
                    image_url = img_element.get_attribute('src')
                except:
                    # Image not found, but continue to extract name
                    pass
                
                # Extract name (this should always work if page loaded)
                name = None
                try:
                    # Wait a bit for page content to load
                    time.sleep(0.5)
                    all_tds = driver.find_elements(By.TAG_NAME, "td")
                    for td in all_tds:
                        text = td.text.strip()
                        if text and 5 < len(text) < 50 and text.replace(' ', '').isalpha():
                            name = text
                            break
                except:
                    pass
                
                # Determine success level and log accordingly
                if image_url and name:
                    print(f"✓ {student_id}: {name} (with image)")
                    return student_id, image_url, name
                elif name and not image_url:
                    print(f"⚠ {student_id}: {name} (⚠️ IMAGE UNAVAILABLE)")
                    return student_id, None, name
                elif image_url and not name:
                    print(f"⚠ {student_id}: Name unknown (image available)")
                    return student_id, image_url, "Unknown"
                else:
                    # Both failed, continue to retry
                    raise Exception("Could not extract name or image")
                
            except Exception as e:
                if attempt < retry_count:
                    print(f"⚠ Retry {attempt + 1}/{retry_count} for {student_id}")
                    time.sleep(1)
                    # Try different proxy on retry
                    proxy = random.choice(self.proxies) if self.proxies else None
                else:
                    print(f"✗ FAILED {student_id}: Could not load page or extract data")
                    return student_id, None, None
            
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
        return student_id, None, None

    def scrape_multiple(self, student_ids: List[str]) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """
        Scrape multiple student IDs in parallel
        
        Args:
            student_ids: List of student IDs to scrape
            
        Returns:
            List of tuples (student_id, image_url, name)
        """
        results = []
        start_time = time.time()
        
        print(f"Starting parallel scraping of {len(student_ids)} students with {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_id = {
                executor.submit(self.extract_student_data, student_id): student_id 
                for student_id in student_ids
            }
            
            # Process completed tasks
            for future in as_completed(future_to_id):
                result = future.result()
                results.append(result)
        
        elapsed = time.time() - start_time
        success_count = sum(1 for _, img_url, _ in results if img_url)
        name_only_count = sum(1 for _, img_url, name in results if not img_url and name)
        total_success = sum(1 for _, img_url, name in results if img_url or name)
        failed_count = len(results) - total_success
        
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {len(results)}")
        print(f"✓ Full success (name + image): {success_count}")
        print(f"⚠️  Partial success (name only, image unavailable): {name_only_count}")
        print(f"✗ Complete failures: {failed_count}")
        print(f"⏱️  Time: {elapsed:.2f}s ({elapsed/len(student_ids):.2f}s per student)")
        print(f"🚀 Speed improvement: ~{4/(elapsed/len(student_ids)):.1f}x faster")
        print(f"{'='*60}")
        
        return results

    def extract_student_image_and_name(self, enrollment_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract student image and name for a single enrollment ID
        Compatible with legacy code expecting (image_url, name) output
        
        Args:
            enrollment_id: Student enrollment/ID number
            
        Returns:
            Tuple of (image_url, name) - either can be None if unavailable
        """
        _, image_url, name = self.extract_student_data(enrollment_id, retry_count=2)
        return image_url, name

    def download_image(self, image_url: str, filename: str) -> bool:
        """Download image from URL"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Optional: Add your proxies here (free or paid)
    # proxies = [
    #     'http://proxy1.example.com:8080',
    #     'http://proxy2.example.com:8080',
    #     'socks5://proxy3.example.com:1080',
    # ]
    proxies = []  # No proxies by default
    
    # Initialize scraper with 5 parallel workers
    scraper = ProxyScraper(proxies=proxies, max_workers=5)
    
    # ============================================================
    # OPTION 1: Single student (legacy compatible format)
    # ============================================================
    print("Testing single student scraping...")
    enrollment_id = "09518241723"
    image_url, name = scraper.extract_student_image_and_name(enrollment_id)
    
    if image_url:
        print(f"Result: image={image_url}, name={name}")
    elif name:
        print(f"Result: image=None, name={name} (Image unavailable)")
    else:
        print(f"Result: image=None, name=None (Failed)")
    
    print("\n" + "="*60 + "\n")
    
    # ============================================================
    # OPTION 2: Multiple students (parallel scraping)
    # ============================================================
    print("Testing parallel scraping...")
    student_ids = [
        "09518241723",
        "09518241724",
        "09518241725",
        "09518241726",
        "09518241727",
    ]
    
    # Scrape in parallel
    results = scraper.scrape_multiple(student_ids)
    
    # Process results
    print("\nDetailed Results:")
    for student_id, image_url, name in results:
        if image_url and name:
            print(f"✓ {student_id} - {name}: {image_url}")
            # Optional: Download image
            # scraper.download_image(image_url, f"{student_id}.jpg")
        elif name and not image_url:
            print(f"⚠️  {student_id} - {name}: NO IMAGE AVAILABLE")
        else:
            print(f"✗ {student_id} - COMPLETELY FAILED")


