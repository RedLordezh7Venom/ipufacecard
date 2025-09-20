from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd

# Read CSV file
df = pd.read_csv('data/alldata.csv')

# URL template
url_template = "https://www.ipuranklist.com/ranklist/{Course}?batch={batch}&insti={Collegeid}&sem=0&branch={Branch}"

# Set up headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)

# Output CSV
output_file = 'enrollments.csv'
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Enrollment Number", "Course", "Batch", "College ID", "Branch"])

    # Loop through each row in DataFrame
    for idx, row in df.iterrows():
        url = url_template.format(
            Course=row['Course'],
            batch=22,
            Collegeid=row['Collegeid'],
            Branch=row['Branch']
        )

        try:
            driver.get(url)
            time.sleep(5)  # Simple wait; use WebDriverWait for production

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            enrollment_numbers = soup.find_all('td', class_='limit-char')

            for number in enrollment_numbers:
                enrollment_number = number.get_text(strip=True)
                writer.writerow([
                    enrollment_number,
                    row['Course'],
                    22,
                    row['Collegeid'],
                    row['Branch']
                ])
            print(f"Scraped: {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

driver.quit()
print(f"Done. Data saved to '{output_file}'.")
