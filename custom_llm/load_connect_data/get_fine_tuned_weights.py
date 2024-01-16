from google.cloud import storage
import boto3
import streamlit as st
import os
import json


# Ensure the directory exists
os.makedirs('tmp/adapters', exist_ok=True)
def upload_adapters_local():
    adapter_model_bin = st.text_input("Adapter .bin path", key="bin_path")
    adapter_model_json = st.text_input("Adapter .json path", key="json_path")
    return adapter_model_bin,adapter_model_json
    
def upload_adapters_aws():
    ###AWS####
    aws_key_id = st.text_input("AWS Key ID", key="aws_key_id")
    aws_secret_access_key = st.text_input("AWS Secret Access Key", type="password", key="aws_secret_access_key")
    region = st.text_input("Region", key="region")
    bucket = st.text_input("Bucket", key="bucket")
    adapter_model_bin = st.text_input("Adapter .bin path", key="bin_path")
    adapter_model_json = st.text_input("Adapter .json path", key="json_path")
    # Initialize a session using your AWS credentials
    aws_session = boto3.Session(
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region  # e.g., us-west-1
    )

    # Initialize the S3 client
    s3 = aws_session.client('s3')

    # Define the bucket name and object key
    bucket_name = bucket
    model_file_key = adapter_model_bin
    config_file_key = adapter_model_json

    # Download files
    s3.download_file(bucket_name, model_file_key, 'tmp/adapters/adapter_model.bin')
    s3.download_file(bucket_name, config_file_key, 'tmp/adapters/adapter_config.json')


def upload_adapters_gcp():
    uploaded_file = st.file_uploader("Upload Service Account JSON", type="json", key="service_account_file")
    service_account_info = None  # Initialize to None
    service_account_info = json.load(uploaded_file)

    if uploaded_file is not None:
        # Initialize a client with the service account info
        storage_client = storage.Client.from_service_account_info(service_account_info)
        

    # Define the bucket name and object name
    bucket_name = st.text_input("Bucket Name", key="bucket_name") 
    adapter_model_bin = st.text_input("Adapter .bin path", key="bin_path")
    adapter_model_json = st.text_input("Adapter .json path", key="json_path")

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Download files
    blob = bucket.blob(adapter_model_bin)
    blob.download_to_filename('tmp/adapters/adapter_model.bin')

    blob = bucket.blob(adapter_model_json)
    blob.download_to_filename('tmp/adapters/adapter_config.json')
