import streamlit as st
import json
import toml

st.markdown("# Load Credentials 🔑")

# Read existing secrets if available
try:
    with open('secrets.toml', 'r') as file:
        existing_secrets = toml.load(file)
except FileNotFoundError:
    existing_secrets = {}

# Global API keys input
hugging_face_token = st.text_input(
    "Hugging Face Token", 
    value=existing_secrets.get("api_keys", {}).get("hugging_face_token", ""), 
    key="global_hugging_face_token"
)
openai_token = st.text_input(
    "OpenAI Token", 
    value=existing_secrets.get("api_keys", {}).get("openai_token", ""), 
    key="global_openai_token"
)

# Function to update the secrets file
def update_secrets_file(updated_data):
    # Merge the existing secrets with the updated data
    existing_secrets.update(updated_data)

    # Write the updated secrets to the TOML file
    with open('secrets.toml', 'w') as file:
        toml.dump(existing_secrets, file)
        

# Function to collect form data
def collect_form_data(form_name):
    st.write(f"Please enter your {form_name} connection details:")
    subsection_name = st.text_input(f"{form_name} Connection Name", key=f"{form_name}_connection_name")
    data = {}

    if form_name == "SQL":
        data = {
            "db_type": st.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQLite"], key=f"{form_name}_db_type"),
            "host": st.text_input("Host", key=f"{form_name}_host"),
            "port": st.text_input("Port", key=f"{form_name}_port"),
            "database": st.text_input("Database Name", key=f"{form_name}_database"),
            "user": st.text_input("User", key=f"{form_name}_user"),
            "password": st.text_input("Password", type="password", key=f"{form_name}_password")
        }
    elif form_name == "AWS":
        data = {
            "aws_key_id": st.text_input("AWS Key ID", key=f"{form_name}_aws_key_id"),
            "aws_secret_access_key": st.text_input("AWS Secret Access Key", type="password", key=f"{form_name}_aws_secret_access_key"),
            "region": st.text_input("Region", key=f"{form_name}_region"),
            "bucket": st.text_input("Bucket", key=f"{form_name}_bucket"),
            "data_path":st.text_input("Data Path", key=f"{form_name}_data_path")
        }
    elif form_name == "GCP BIGQUERY":
        data = {
            "type": "BigQuery",
            "project_id": st.text_input("Project ID", key=f"{form_name}_project_id"),
            "schema": st.text_input("Schema", key=f"{form_name}_schema"),
            "table": st.text_input("Table", key=f"{form_name}_table")
        }
         # File uploader for service account JSON
        uploaded_file = st.file_uploader("Upload Service Account JSON", type="json", key=f"{form_name}_service_account_file")
        if uploaded_file is not None:
            # Read the JSON file
            service_account_info = json.load(uploaded_file)
            # Store the service account info in the data dictionary
            data["service_account_key"] = service_account_info
    elif form_name == "GCP BUCKETS":
        data = {
            "type": "Buckets",
            "project_id": st.text_input("Project ID", key=f"{form_name}_project_id"),
            "bucket_name": st.text_input("Bucket Name", key=f"{form_name}_bucket_name"),
            "object_name": st.text_input("Object Name", key=f"{form_name}_object_name")
        }
         # File uploader for service account JSON
        uploaded_file = st.file_uploader("Upload Service Account JSON", type="json", key=f"{form_name}_service_account_file")
        if uploaded_file is not None:
            # Read the JSON file
            service_account_info = json.load(uploaded_file)
            # Store the service account info in the data dictionary
            data["service_account_key"] = service_account_info
            
    

    return {f"{form_name.lower()}.{subsection_name}": data}

# Process each form
for form_name in ["SQL", "AWS", "GCP BIGQUERY","GCP BUCKETS"]:
    with st.form(f"{form_name.lower()}_connection_form"):
        form_data = collect_form_data(form_name)
        submitted = st.form_submit_button(f"Submit {form_name}")
        if submitted and form_data:
            update_secrets_file(form_data)

# Update global API keys if changed
api_keys = {"api_keys": {}}
if hugging_face_token != existing_secrets.get("api_keys", {}).get("hugging_face_token", ""):
    api_keys["api_keys"]["hugging_face_token"] = hugging_face_token
    update_secrets_file(api_keys)

if openai_token != existing_secrets.get("api_keys", {}).get("openai_token", ""):
    api_keys["api_keys"]["openai_token"] = openai_token
    update_secrets_file(api_keys)
