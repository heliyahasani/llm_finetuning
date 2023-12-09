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

st.markdown("# Load or Connect Your Data")

# Load the TOML file
with open('secrets.toml', 'r') as file:
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
    except Error as e:
        st.error(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def connect_bigquery(secrets, section, query):
    credentials = service_account.Credentials.from_service_account_file(secrets[section]["service_account_json_path"])
    client = bigquery.Client(credentials=credentials, project=secrets[section]["project_id"])
    schema = secrets[section]["schema"]
    table = secrets[section]["table"]
    st.write(f"Please use schema: {schema} and table: {table}")
    query_job = client.query(query)
    df = query_job.to_dataframe()
    st.write(df.head(10))

def connect_aws(secrets, section):
    boto3.setup_default_session(aws_access_key_id=secrets[section]["aws_access_key_id"], aws_secret_access_key=secrets[section]["aws_secret_access_key"], region_name=secrets[section]["region"])
    df = wr.s3.read_csv(f's3://{secrets[section]["bucket"]}/{secrets[section]["data_path"]}')
    st.write(df.head(10))

def handle_saved_query(secrets, section, query):
    saved_query = st.selectbox("Would you like to save those as a data source?", ["Yes", "No"], key=f"{section}_saved_query")
    if saved_query == "Yes":
        secrets[section]["sql"] = query
        with open('secrets.toml', 'w') as file:
            toml.dump(secrets, file)
            
def handle_local_files():
    local_directory = "/tmp/llm"
    os.makedirs(local_directory, exist_ok=True)
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        local_file_path = os.path.join(local_directory, uploaded_file.name)
        with open(local_file_path, 'wb') as file:
            file.write(uploaded_file.getvalue())
        st.success(f"File '{uploaded_file.name}' has been saved locally at {local_file_path}")


load_data = st.selectbox("Where to load data?", ["Local", "AWS", "GCP", "Postgres", "MySQL"])

if load_data == "Local":
    handle_local_files()
elif load_data == "AWS":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "aws" in section], key="aws_configuration")
    connect_aws(secrets, configuration)
elif load_data == "GCP":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "gcp" in section], key="gcp_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        connect_bigquery(secrets, configuration, query=query)
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "Postgres":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "sql" in section and secrets[section].get("db_type") == "PostgreSQL"], key="postgres_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        connect_postgres(secrets, configuration, query=query)
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "MySQL":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "sql" in section and secrets[section]["db_type"] == "MySQL"], key="mysql_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        connect_mysql(secrets, configuration, query=query)
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")

