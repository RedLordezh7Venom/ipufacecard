from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import time

# Set up headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
url = "https://www.ipuranklist.com/ranklist/mba?batch=20&branch=GENERAL&insti=123&sem=0"

# Open the page
driver.get(url)
time.sleep(5)  # You can use WebDriverWait for smarter waiting
html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')

enrollment_numbers = soup.find_all('td', class_='limit-char')

# Write data to CSV
with open('enrollment_numbers.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Enrollment Number"])

    for number in enrollment_numbers:
        enrollment_number = number.get_text(strip=True)
        writer.writerow([enrollment_number])

print("Enrollment numbers have been saved to 'enrollment_numbers.csv'.")
