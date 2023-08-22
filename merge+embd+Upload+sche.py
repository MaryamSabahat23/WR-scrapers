
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

# List of URLs for each platform
indeed_urls = [
    "https://uk.indeed.com/jobs?q=hospitality&l=United+Kingdom&fromage=14&vjk=2195bd2e0db5e116",
    "https://au.indeed.com/jobs?q=hospitality&l=sydney&fromage=14&vjk=a1204f66b0f48232"
]

glassdoor_urls = [
    "https://www.glassdoor.com/Job/united-kingdom-hospitality-jobs-SRCH_IL.0,14_IN2_KO15,26_IP{page}.htm?includeNoSalaryJobs=true&fromAge=14&pgc=AB4AAYEAHgAAAAAAAAAAAAAAAgu%2BOz4AQgEBAQcB5G2fcBtRXtIa%2BB5gxx9gNtA7YJOIlCbGJBJeX%2BYrBPw6Zn9iS1JgWrYxW%2FPoFMEtBJKiA7pVIaDf8MEtsQAA",
    "https://www.glassdoor.com.au/Job/australia-hospitality-jobs-SRCH_IL.0,9_IN16_KO10,21.htm?fromAge=14"
]

seek_base_url = "https://www.seek.com.au/hospitality-jobs/in-sydney?page={page}"

# Create an empty list to store all job data
all_job_data = []

# Create an empty dictionary to store job title counts
job_title_counts = {}

# Initialize time
current_time = int(time.time())

# Loop through Indeed URLs
for indeed_url in indeed_urls:
    for page in range(1, 20):  # Change '6' to the desired number of pages
        current_url = indeed_url.format(page=page)
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

                all_job_data.append({
                    "job_title": job_title,
                    "job_data": job_data,
                    "job_url": job_url
                })

                if job_title not in job_title_counts:
                    job_title_counts[job_title] = 1
                else:
                    job_title_counts[job_title] += 1

            time.sleep(3)  # Add a delay before navigating to the next page

# Loop through Glassdoor URLs
for glassdoor_url in glassdoor_urls:
    for page in range(1, 20):  # Change '6' to the desired number of pages
        current_url = glassdoor_url.format(page=page)
        driver.get(current_url)

        # Wait for job cards to be loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'react-job-listing')]"))
        )

        job_cards = driver.find_elements(By.XPATH, "//li[contains(@class, 'react-job-listing')]")

        for card in job_cards:
            job_data = card.text.strip()
            job_title = job_data.split('\n')[1]  # Assuming the job role is the second line

            job_url_element = card.find_element(By.TAG_NAME, "a")
            job_url = job_url_element.get_attribute('href')

            all_job_data.append({
                "job_title": job_title,
                "job_data": job_data,
                "job_url": job_url
            })

            if job_title not in job_title_counts:
                job_title_counts[job_title] = 1
            else:
                job_title_counts[job_title] += 1

            time.sleep(3)  # Add a delay before navigating to the next page

# Loop through Seek pages
for page in range(1, 20):  # Modify the range accordingly
    if time.time() - current_time >= 500:
        break

    seek_url = seek_base_url.format(page=page)
    driver.get(seek_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//article[@data-automation='normalJob']"))
    )

    job_cards = driver.find_elements(By.XPATH, "//article[@data-automation='normalJob']")

    for card in job_cards:
        job_data = card.text.strip()
        job_title = job_data.split('\n')[1]

        job_url_element = card.find_element(By.XPATH, ".//a[contains(@data-automation, 'jobTitle')]")
        job_url = job_url_element.get_attribute('href')

        all_job_data.append({
            "job_title": job_title,
            "job_data": job_data,
            "job_url": job_url
        })

        if job_title not in job_title_counts:
            job_title_counts[job_title] = 1
        else:
            job_title_counts[job_title] += 1

        time.sleep(3)

# Close the driver
driver.quit()

# Combine job data and job title counts into a dictionary
combined_data = {
    "job_data": all_job_data,
    "job_title_counts": job_title_counts
}

# Write the combined job data to a single JSON file
output_file = f"combined_job_data_{current_time}.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(combined_data, file, indent=4)

# Print job title counts
print("Job Title Counts:")
for job_title, count in job_title_counts.items():
    print(f"{job_title}: {count} jobs")

print(f"Scraped {len(all_job_data)} job listings and saved to {output_file}")









"""embedding + Uploading in BLOB"""





import datetime
from azure.storage.blob import BlobServiceClient, ContainerClient
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import openai
import json
from langchain.document_loaders import TextLoader

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DEPLOYMENT_ENDPOINT = os.getenv("OPENAI_DEPLOYMENT_ENDPOINT")
OPENAI_DEPLOYMENT_VERSION = os.getenv("OPENAI_DEPLOYMENT_VERSION")

# Assuming you have the json_data variable containing the extracted JSON data
json_data = "output_file"  # Insert your extracted JSON data here
txt_file = 'data.txt'

def convert_json_to_txt(json_data, txt_file):
    # Convert the JSON data to a string representation
    text_content = json.dumps(json_data, indent=2)

    # Write the text content to the TXT file
    with open(txt_file, 'w', encoding='utf-8') as file:
        file.write(text_content)

# Convert JSON to TXT
convert_json_to_txt(json_data, txt_file)

# Initialize Azure OpenAI
openai.api_type = "azure"
openai.api_version = OPENAI_DEPLOYMENT_VERSION
openai.api_base = OPENAI_DEPLOYMENT_ENDPOINT
openai.api_key = OPENAI_API_KEY

if __name__ == "__main__":
    # Provide your OpenAI API key
    openai_api_key = OPENAI_API_KEY

    # Initialize OpenAI Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, chunk_size=1)

    fileName = txt_file  # Use the same file name for embedded files

    # Use Langchain TXT loader
    loader = TextLoader(fileName)

    # Split the document into chunks (pages)
    pages = loader.load_and_split()

    # Use Langchain to create the embeddings using text-embedding-ada-002
    db = FAISS.from_documents(documents=pages, embedding=embeddings)

    # Save the embeddings into FAISS vector store using the same name
    output_dir = "./embeddedData/"
    output_file_name = os.path.splitext(os.path.basename(txt_file))[0]
    db.save_local(os.path.join(output_dir, output_file_name))

    # Upload the embedded folder to Azure Blob Storage
    connection_string = "DefaultEndpointsProtocol=https;AccountName=cbconversationdata;AccountKey=IF5dtYVJJrMuMqKUP2aP1q+pYopOg9OGQX2PLy+/b1hSLIi5mRKb3hfNhF5hVGf3qUSzEhMk70qp+AStIQDwOA==;EndpointSuffix=core.windows.net"
    container_name = "embedded-data"

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Generate a unique name for the embedded data using the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{output_file_name}_{timestamp}"

    # Upload the embedded folder to Azure Blob Storage with the unique name
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            blob_name = f"{unique_name}/{file}"  # Include the unique name in the blob path
            blob_client = container_client.get_blob_client(blob_name)
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data)

            print(f"Uploaded {local_file_path} to {blob_name} in container {container_name}")













"""schedular"""
import schedule
import time
import subprocess

def run_script(script_path):
    print(f"Running script: {script_path}")
    subprocess.run(["python", script_path])
    print(f"Script {script_path} executed.")

#  Schedule the scripts to run every 1 **minute"
schedule.every(7).days.do(run_script, script_path="merge+embd+Upload+sche.py")

while True:
    schedule.run_pending()
    time.sleep(1)


