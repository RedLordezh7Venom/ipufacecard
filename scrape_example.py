import requests
from bs4 import BeautifulSoup
import csv

# URL of the page to scrape
url = "https://www.ipuranklist.com/ranklist/mba?batch=20&branch=GENERAL&insti=123&sem=0"

# Send HTTP request to the URL
response = requests.get(url)

# Check if request was successful (status code 200)
if response.status_code == 200:
    print("Page successfully fetched.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")
    exit()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all <td> tags with the class "limit-char" containing the enrollment numbers
enrollment_numbers = soup.find_all('td', class_='limit-char')

# Open a CSV file to save the data
with open('enrollment_numbers.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Enrollment Number"])  # Write the header

    # Loop through each enrollment number and write it to the CSV file
    for number in enrollment_numbers:
        enrollment_number = number.get_text(strip=True)
        writer.writerow([enrollment_number])

print("Enrollment numbers have been saved to 'enrollment_numbers.csv'.")
