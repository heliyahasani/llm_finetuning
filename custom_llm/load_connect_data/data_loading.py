import streamlit as st
import pandas as pd
import toml
import os
import json
import psycopg2
import mysql.connector
from mysql.connector import Error
from google.cloud import bigquery
from google.oauth2 import service_account
import boto3
import awswrangler as wr
from google.cloud import storage
from pathlib import Path
import tempfile
from datasets import Dataset


st.markdown("# Load Data")

# Load the TOML file
with open(r'/home/heliya/llm_finetuning/custom_llm/secrets.toml', 'r') as file:
    secrets = toml.load(file)
section_names = secrets.keys()

def connect_postgres(secrets, section, query):
    try:
        conn = psycopg2.connect(
            database=secrets[section]["database"],
            user=secrets[section]["user"],
            password=secrets[section]["password"],
            host=secrets[section]["host"],
            port=secrets[section]["port"]
        )
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        st.write(df.head(10))
        handle_saved_query(secrets, section, query)
        column = st.selectbox("Which column should be used for inference?", df.columns)
        df = df.rename(columns={column: "text"})
        return df[[column]]
    except psycopg2.Error as e:
        st.error(f"Error connecting to PostgreSQL: {e}")
    finally:
        conn.close()

def connect_mysql(secrets, section, query):
    try:
        connection = mysql.connector.connect(
            host=secrets[section]["host"],
            database=secrets[section]["database"],
            user=secrets[section]["user"],
            password=secrets[section]["password"],
            port=secrets[section]["port"]
        )
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        st.write(df.head(10))
        handle_saved_query(secrets, section, query)
        column = st.selectbox("Which column should be used for inference?", df.columns)
        df = df.rename(columns={column: "text"})
        return df[["text"]]

    except Error as e:
        st.error(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def connect_bigquery(secrets, section, query):
 # Convert the dictionary to a JSON string
    credentials_json = json.dumps(secrets[section]["service_account_key"])
    # Create credentials from the JSON string
    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
    # Create a client using the credentials
    client = bigquery.Client(credentials=credentials, project=secrets[section]["project_id"])
    schema = secrets[section]["schema"]
    table = secrets[section]["table"]
    st.write(f"Please use schema: {schema} and table: {table}")
    query_job = client.query(query)
    df = query_job.to_dataframe()
    st.write(df.head(10))
    column = st.selectbox("Which column should be used for inference?", df.columns)
    df = df.rename(columns={column: "text"})
    return df[["text"]]

def connect_bucket(secrets, section):
    try:
        # Convert the dictionary to a JSON string
        credentials_json = json.dumps(secrets[section]["service_account_key"])
        # Create credentials from the JSON string
        credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
        # Create a client using the credentials
        client = storage.Client(credentials=credentials)
        bucket = client.get_bucket(secrets[section]["bucket_name"])
        # Get the blob (object) from the bucket
        blob = bucket.blob(secrets[section]["object_name"])
        # Create a temporary file to store the downloaded data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            # Download the blob data to the temporary file
            blob.download_to_file(temp_file)
        
        # Read the temporary CSV file into a DataFrame
        df = pd.read_csv(temp_file.name)
        st.write(df.head(10))
        column = st.selectbox("Which column should be used for inference?", df.columns)
        df = df.rename(columns={column: "text"})
        return df[["text"]]
    
    except Exception as e:
        st.write(f"Error: {e}")

    
def connect_aws(secrets, section):
    boto3.setup_default_session(aws_access_key_id=secrets[section]["aws_access_key_id"], aws_secret_access_key=secrets[section]["aws_secret_access_key"], region_name=secrets[section]["region"])
    df = wr.s3.read_csv(f's3://{secrets[section]["bucket"]}/{secrets[section]["data_path"]}')
    st.write(df.head(10))
    column = st.selectbox("Which column should be used for inference?", df.columns)
    df = df.rename(columns={column: "text"})
    return df[["text"]]

def handle_saved_query(secrets, section, query):
    saved_query = st.selectbox("Would you like to save those as a data source?", ["Yes", "No"], key=f"{section}_saved_query")
    if saved_query == "Yes":
        secrets[section]["sql"] = query
        with open('secrets.toml', 'w') as file:
            toml.dump(secrets, file)
            
def handle_local_files():
    uploaded_file = st.file_uploader("Choose a file")
    
    if uploaded_file is not None:
        df = load_file_to_dataframe(uploaded_file)
        st.write(df.head(10))  # Display the first 10 rows of the DataFrame
        column = st.selectbox("Which column should be used for inference?", df.columns)
        df = df.rename(columns={column: "text"})
        return df[["text"]]

       
def load_file_to_dataframe(file):
    # Determine the file type from the extension
    file_extension = file.name.split('.')[-1]
    
    # Read the file based on its file type
    if file_extension == 'csv':
        return pd.read_csv(file)
    elif file_extension == 'parquet':
        return pd.read_parquet(file)
    elif file_extension in ['txt', 'log']:
        return pd.read_csv(file, header=None, names=['data'])
    elif file_extension in ['xlsx', 'xls']:
        return pd.read_excel(file)
    elif file_extension == 'json':
        return pd.read_json(file)
    else:
        st.write("Unexpected file extension.")
