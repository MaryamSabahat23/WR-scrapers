import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from collections import Counter
import os
from azure.storage.blob import BlobServiceClient


# Set up Chrome options with the extension
chrome_options = Options()
# chrome_options.add_extension(extension_path)

# Create Chrome WebDriver with the specified options
driver = webdriver.Chrome(options=chrome_options)

# Get the current timestamp
current_time = int(time.time())

# Create a new JSON file for output with a unique timestamp in the filename
output_file = f"seek_jobs_{current_time}.json"

# Create an empty list to store job data
job_data_list = []

# Create an empty dictionary to store job title counts
job_title_counts = {}

# Loop through the pages (modify based on Seek's pagination structure) or until a certain condition
for page in range(1, 26):  # Adjust the range accordingly
    # Check if a certain condition is met to break the loop
    if time.time() - current_time >= 500:
        break

    # Navigate to the Seek URL for each page
    url = f"https://www.seek.com.au/hospitality-jobs/in-sydney?page={page}"  # Modify the URL structure
    driver.get(url)

    # Wait for job cards to be loaded (modify based on Seek's job card structure)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//article[@data-automation='normalJob']"))
    )

    # Find all job cards on the page using the provided XPath expression
    job_cards = driver.find_elements(By.XPATH, "//article[@data-automation='normalJob']")

    # Loop through the job cards
    for card in job_cards:
        # Get the job data
        job_data = card.text.strip()

        # Extract the job title (including job role)
        job_title = job_data.split('\n')[1]  # Assuming the job role is the second line

        # Count the job title occurrence in the dictionary
        if job_title in job_title_counts:
            job_title_counts[job_title] += 1
        else:
            job_title_counts[job_title] = 1

        # Get the job URL
        job_url_element = card.find_element(By.XPATH, ".//a[contains(@data-automation, 'jobTitle')]")
        job_url = job_url_element.get_attribute('href')

        # Append job title, job data, and job URL to the list
        job_data_list.append({
            "job_title": job_title,
            "job_data": job_data,
            "job_url": job_url
        })

    # Add a small delay before navigating to the next page (optional, adjust as needed)
    time.sleep(3)

# Print the job titles with their counts
for job_title, count in job_title_counts.items():
    print(f"{job_title}: {count} jobs")

# Write the job data list to the JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(job_data_list, file, indent=4)

# Close the driver
driver.quit()

print(f"Scraped {len(job_data_list)} job listings and saved to {output_file}")









# Your Azure Blob Storage connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=cbconversationdata;AccountKey=IF5dtYVJJrMuMqKUP2aP1q+pYopOg9OGQX2PLy+/b1hSLIi5mRKb3hfNhF5hVGf3qUSzEhMk70qp+AStIQDwOA==;EndpointSuffix=core.windows.net"

# Your container name
container_name = "seek-aus-data"

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get the current timestamp
current_time = int(time.time())

# Create a new JSON file for output with a unique timestamp in the filename
output_file = f"seek_jobs_{current_time}.json"

# Write the job data list to the JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(job_data_list, file, indent=4)

# Get the BlobClient for the output file
blob_client = blob_service_client.get_blob_client(container=container_name, blob=output_file)

# Upload the file to Azure Blob Storage
with open(output_file, "rb") as data:
    blob_client.upload_blob(data)

# Delete the local file after uploading
os.remove(output_file)

print(f"Scraped {len(job_data_list)} job listings and saved to Azure Blob Storage container: {container_name}")
