import os
import json
import psycopg2
from google.cloud import storage
import time




# Constants for PostgreSQL and Google Cloud credentials and connection details
PG_HOST = 'localhost'
PG_PORT = '5432'
PG_DATABASE = 'question_bank'
PG_USER = 'chightower'
PG_PASSWORD = 'Wellpleased22!'
GC_BUCKET_NAME = 'question_bank_files'



# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    host=PG_HOST,
    port=PG_PORT
)
cur = conn.cursor()



# Function to create table
def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions_db (
            id SERIAL PRIMARY KEY,
            topic VARCHAR(255),
            sub_topic VARCHAR(255),
            content JSONB
        );
    """)
    conn.commit()

create_table()  # Create the table if it doesn't exist



# Instantiate a Google Cloud Storage client and retrieve the bucket
# Connect to Google Cloud Storage
# Path to the service account key .json file
key_path = 'qb_and_pt_files_service_account.json'

# Instantiate a Google Cloud Storage client with the credentials
storage_client = storage.Client.from_service_account_json(key_path)
bucket = storage_client.get_bucket(GC_BUCKET_NAME)


url_list = []
# Function to upload files to Google Cloud Storage and get the file path
def upload_to_gcs(file_path):

    # Create a blob object from the file path
    blob = bucket.blob(file_path)
    # Check if the blob already exists
    if blob.name not in url_list:
        # If not, upload the file
        blob.upload_from_filename(file_path)
        print(f"Blob {file_path} uploaded to bucket.")
        url_list.append(blob.name)
        time.sleep(7)
    else:
        print(f"Blob {file_path} already exists in the bucket.")
    
    # Return the public URL
    return f"https://storage.googleapis.com/{GC_BUCKET_NAME}/{blob.name}"

# Function to insert JSON into the PostgreSQL database
def insert_json_to_db(question_dict, topic, sub_topic):
    json_content = json.dumps(question_dict)
    cur.execute(
        "INSERT INTO questions_db (topic, sub_topic, content) VALUES (%s, %s, %s)",
        (topic, sub_topic, json_content)
    )
    conn.commit()
    print(f"json content for {topic, sub_topic} added to DB")

# Function to update JSON with new SVG path
def update_file_path(json_content):
    for question in json_content.values():
        if 'svg' in question:
            svg_path = question['svg']
            svg_url = upload_to_gcs(svg_path)
            question['svg'] = svg_url
            print(f"json key value updated to {svg_url}")
        if 'image' in question:
            image_path = question['image']
            print(image_path)
            image_url = upload_to_gcs(image_path)
            question['image'] = image_url
            print(f"json key value updated to {image_url}")
    return json_content

# Main function to process the JSON files and upload to GCS and PostgreSQL
def process_files(root_dir):
    for dirpath, dirs, files in os.walk(root_dir): 
        # walk_exp = """
        # dirpath, dirnames, filenames --> dirpath is a string, the path to the directory. dirnames is a list of the names of the subdirectories in dirpath (including symlinks to directories, and excluding '.' and '..'). 
        # filenames is a list of the names of the non-directory files in dirpath.
        #   Note that the names in the lists are just names, with no path components. To get a full path (which begins with top) to a file or directory in dirpath, do os.path.join(dirpath, name).
        # """
        topic = os.path.basename(dirpath)
        for file in files:
            file_path = os.path.join(dirpath, file)
            if file_path.endswith('.json'):
                with open(file_path, 'r') as json_file:
                    json_content = json.load(json_file)
                    updated_content = update_file_path(json_content)
                    sub_topic = file.replace(".json", "")
                    insert_json_to_db(updated_content, topic, sub_topic)


process_files("question_bank")

# Close PostgreSQL connection
cur.close()
conn.close()
