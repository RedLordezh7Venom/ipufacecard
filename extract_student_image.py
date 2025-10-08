import requests
from bs4 import BeautifulSoup

def extract_student_image(student_id):
    url = f"https://www.ipuranklist.com/student/{student_id}"
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        
        # Find the image element with the specific attribute
        img_tag = soup.find('img')
        
        if img_tag and 'src' in img_tag.attrs:
            image_url = img_tag['src']
            print(f"Image URL found: {image_url}")
            return image_url
        else:
            print("Image not found on the page.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

# Example usage
if __name__ == "__main__":
    student_id = "09518241723"  # Replace with any student ID
    image_url = extract_student_image(student_id)
    
    if image_url:
        # If you want to download the image
        print(image_url)