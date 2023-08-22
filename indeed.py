import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
from collections import Counter
from azure.storage.blob import BlobServiceClient

# Set up Chrome options
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

# List of URLs to scrape
urls = [
    "https://uk.indeed.com/jobs?q=hospitality&l=United+Kingdom&fromage=14&vjk=2195bd2e0db5e116",
    "https://au.indeed.com/jobs?q=hospitality&l=sydney&fromage=14&vjk=a1204f66b0f48232"
]

# Create a BlobServiceClient object
connection_string = "DefaultEndpointsProtocol=https;AccountName=cbconversationdata;AccountKey=IF5dtYVJJrMuMqKUP2aP1q+pYopOg9OGQX2PLy+/b1hSLIi5mRKb3hfNhF5hVGf3qUSzEhMk70qp+AStIQDwOA==;EndpointSuffix=core.windows.net"
container_name = "indeed-data"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create an empty list to store job data
job_data_list = []

# Create a Counter to count job titles
job_title_counter = Counter()

# Loop through the URLs
for url in urls:
    # Loop through the pages
    for page in range(1, 30):  # Adjust the range accordingly
        current_url = url.format(page=page * 10)
        driver.get(current_url)

        # Wait for job cards to be loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'job_seen_beacon')]"))
        )

        job_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'job_seen_beacon')]")

        for card in job_cards:
            job_data = card.text.strip()
            lines = job_data.split('\n')

            if len(lines) >= 2:
                job_title_element = card.find_element(By.XPATH, ".//h2[contains(@class, 'jobTitle')]")
                job_title = job_title_element.text

                job_url_element = card.find_element(By.TAG_NAME, "a")
                job_url = job_url_element.get_attribute('href')

                job_data_list.append({
                    "job_title": job_title,
                    "job_data": job_data,
                    "job_url": job_url
                })

                # Count job titles
                job_title_counter[job_title] += 1

        time.sleep(3)  # Add a delay before navigating to the next page

# Close the driver
driver.quit()

# Create a new JSON file for output
current_time = int(time.time())
output_file = f"indeed_jobs_{current_time}.json"

# Write the job data list to the JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(job_data_list, file, indent=4)

# Print the job titles with their counts
for job_title, count in job_title_counter.items():
    print(f"{job_title}: {count} jobs")

# Get the BlobClient for the output file
blob_client = blob_service_client.get_blob_client(container=container_name, blob=output_file)

# Upload the file to Azure Blob Storage
with open(output_file, "rb") as data:
    blob_client.upload_blob(data)

# Delete the local file after uploading
os.remove(output_file)

print(f"Scraped {len(job_data_list)} job listings and saved to Azure Blob Storage container: {container_name}")
