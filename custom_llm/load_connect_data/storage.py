import os
import boto3
from Credidentials import update_secrets_file

from google.cloud import storage
from sqlalchemy import create_engine
from botocore.exceptions import NoCredentialsError
import json
import streamlit as st

###### GCP ########

def create_bucket(storage_data):
    uploaded_file = st.file_uploader("Upload Service Account JSON", type="json", key=f"{storage_data}_service_account_file")
    service_account_info = None  # Initialize to None

    if uploaded_file is not None:
        save = st.selectbox("Would you like to save the credentials??", ["Yes", "No"])
        if save == "Yes":
            # Save the service account JSON to a temporary file
            with open("service_account.json", "w") as json_file:
                json.dump(json.load(uploaded_file), json_file)
            # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the temporary file path
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
            # Read the saved service account info
            with open("service_account.json", "r") as saved_json_file:
                service_account_info = json.load(saved_json_file)

    storage_client = storage.Client()
    bucket = st.selectbox("Would you like to create a new bucket?", ["No", "Yes"])

    if bucket == "No":
        bucket_name = st.text_input("Enter your existing bucket name in GCP?", key="bucket_name")
        return bucket_name, service_account_info
    else:
        bucket_name = st.text_input("Enter your new bucket name?", key="bucket_name")
        storage_class = st.selectbox("Choose storage class", ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"], key="storage_class")
        bucket = storage_client.bucket(bucket_name)
        bucket.storage_class = storage_class
        if not bucket.exists():
            bucket.create()
            st.write(f"Bucket '{bucket_name}' created successfully.")
        return bucket.name, service_account_info

# Function to upload objects to the bucket
def upload_object_to_bucket(storage_data):
    local_directory = "./tmp/results"
    bucket_name, service_account_info = create_bucket(storage_data)  # This returns the service account info
    local_files = os.listdir(local_directory)

    try:
        if service_account_info is not None:
            # Initialize a GCS client with the service account json file path
            client = storage.Client.from_service_account_info(service_account_info)
            # Get a reference to the target GCS bucket
            bucket = client.get_bucket(bucket_name)

            for local_file in local_files:
                local_file_path = os.path.join(local_directory, local_file)
                blob = bucket.blob(local_file)
                blob.upload_from_filename(local_file_path)
                st.write(f"Uploaded {local_file} to GCS bucket.")

        else:
            st.write("No file was uploaded. Please upload a service account JSON file first.")

    except Exception as e:
        st.write(f'Error uploading file: {str(e)}')

###### AWS #######

def upload_to_aws():
    file_to_save = st.selectbox("Which file would you like to save?", ["a", "b","c"])

    s3 = boto3.client('s3')
    bucket_name = st.text_input("Enter your existing bucket name in GCP?", key="bucket_name")
    s3_file = st.file_uploader("Upload Service Account JSON", type="json", key=f"aws_service_account_file")
    if s3_file is not None:
        save = st.selectbox("Would you like to save the credentials??", ["Yes", "No"])
        # Read the JSON file
        service_account_info = json.load(s3_file)
        # Store the service account info in the data dictionary
        if save == "Yes":
            # Assuming you have a function update_secrets_file in a Credentials module
            pass
    try:
        s3.upload_file(file_to_save, bucket_name, s3_file)
        print(f"Upload Successful: {s3_file} has been uploaded to {bucket_name}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

#### SQL #######
df = None 

def upload_sql(storage_data):
    user = st.text_input("User", key="user")
    password = st.text_input("Password", key="password")
    host = st.text_input("Host", key="host")
    port = st.text_input("Port", key="port")
    database = st.text_input("Database", key="bucket_name")
    
    # Check if all fields are filled
    if not user or not password or not host or not port or not database:
        st.warning("Please fill in all the required fields.")
        return  # Stop execution if any field is empty


    if storage_data == "MySQL":
        engine = create_engine(f'mysql+pymysql://{user}:{password}@:{host}:{port}/{database}')
    else:
        engine = create_engine(f'postgresql://{user}:{password}@:{host}:{port}/{database}')
    
    table_name = st.text_input("Table Name", key="table_name")

    df.to_sql(table_name, con=engine, if_exists='replace')
    print("Successfully saved")


