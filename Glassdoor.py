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

# Get the current timestamp
current_time = int(time.time())

# Create a new JSON file for output with a unique timestamp in the filename
output_file = f"glassdoor_data {current_time}.json"

# Create an empty list to store job data
job_data_list = []
# Create an empty dictionary to store job title counts
job_title_counts = {}
# Loop through the pages (up to 30) or until 5 minutes have passed
for page in range(1, 20):
    # Check if 5 minutes have passed, if yes, break the loop
    if time.time() - current_time >= 400:
        break

    # Navigate to the Glassdoor URL for each page
    urls = [
        "https://www.glassdoor.com/Job/united-kingdom-hospitality-jobs-SRCH_IL.0,14_IN2_KO15,26_IP{page}.htm?includeNoSalaryJobs=true&fromAge=14&pgc=AB4AAYEAHgAAAAAAAAAAAAAAAgu%2BOz4AQgEBAQcB5G2fcBtRXtIa%2BB5gxx9gNtA7YJOIlCbGJBJeX%2BYrBPw6Zn9iS1JgWrYxW%2FPoFMEtBJKiA7pVIaDf8MEtsQAA",
        "https://www.glassdoor.com.au/Job/australia-hospitality-jobs-SRCH_IL.0,9_IN16_KO10,21.htm?fromAge=14"
    ]
    for url in urls:
        driver.get(url)  # Change this line to use 'url'
    # Wait for job cards to be loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'react-job-listing')]"))
    )

    # Find all job cards on the page
    job_cards = driver.find_elements(By.XPATH, "//li[contains(@class, 'react-job-listing')]")

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
        job_url_element = card.find_element(By.TAG_NAME, "a")
        job_url = job_url_element.get_attribute('href')

        # Append job data and URL to the list without checking for uniqueness
        job_data_list.append({
            "job_title": job_title,
            "job_data": job_data,
            "job_url": job_url
        })

    # Add a small delay before navigating to the next page (optional, adjust as needed)
    time.sleep(3)

# # Print the job titles with their counts
for job_title, count in job_title_counts.items():
    print(f"{job_title}: {count} jobs")

# Close the driver
driver.quit()


# Write the job data list to the JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(job_data_list, file, indent=4)



print(f"Scraped {len(job_data_list)} job listings and saved to {output_file}")

# Set your Azure Blob Storage credentials
connection_string = "DefaultEndpointsProtocol=https;AccountName=cbconversationdata;AccountKey=IF5dtYVJJrMuMqKUP2aP1q+pYopOg9OGQX2PLy+/b1hSLIi5mRKb3hfNhF5hVGf3qUSzEhMk70qp+AStIQDwOA==;EndpointSuffix=core.windows.net"

# Create a BlobServiceClient using the connection string
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Define the container and blob name
container_name = "glassddoor-data"
blob_name = f"glassdoor-data {current_time}.json"

# Get a reference to the container
container_client = blob_service_client.get_container_client(container_name)

# Upload the JSON file to the container
blob_client = container_client.get_blob_client(blob_name)
with open(output_file, "rb") as data:
    blob_client.upload_blob(data)

# Close the driver
driver.quit()

print(f"Scraped {len(job_data_list)} job listings and saved to {output_file}")
print(f"JSON file '{blob_name}' has been uploaded to the '{container_name}' container in Azure Blob Storage.")