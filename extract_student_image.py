import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


def extract_student_image_and_name(student_id):
    """
    Extract student image URL from IPU Ranklist website using Selenium
    """
    url = f"https://www.ipuranklist.com/student/{student_id}"
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the URL
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for the image to load (wait for img tag with src containing 'assets.ipuranklist.com')
        print("Waiting for image to load...")
        wait = WebDriverWait(driver, 10)
        img_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='assets.ipuranklist.com']"))
        )
        
        # Extract the image URL
        image_url = img_element.get_attribute('src')
        print(f"Image URL found: {image_url}")
        
        # Extract the name - try multiple selectors
        name = None
        try:
            # Try to find the name in the table - look for the first td after "Name" label
            name_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Name')]/following-sibling::td[1]")
            name = name_element.text.strip()
            print(f"Name found: {name}")
        except:
            try:
                # Alternative: Look for any td that contains a name-like pattern (all caps)
                name_element = driver.find_element(By.XPATH, "//table//td[string-length(text()) > 5 and string-length(text()) < 50]")
                name = name_element.text.strip()
                print(f"Name found (alternative): {name}")
            except:
                print("Warning: Could not extract name")
                name = "Unknown"
        
        return image_url, name
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None
        
    finally:
        if driver:
            driver.quit()

def download_image(image_url, filename='student_photo.jpg'):
    """
    Download the image from the URL
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded successfully as '{filename}'")
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

# Example usage
if __name__ == "__main__":
    student_id = "09518241723"  # Replace with any student ID
    image_url, name = extract_student_image_and_name(student_id)
    
    if image_url:
        print(image_url,name)
    else:
        print("Failed to extract image URL")