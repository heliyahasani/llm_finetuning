import streamlit as st
import json
import subprocess
import toml 

st.markdown("# Loaded Sources Overview")
# Load the TOML file
with open('secrets.toml', 'r') as file:
    secrets = toml.load(file)
section_names = secrets.keys()

def local_files():
    # Define the command you want to run
    command = "ls /tmp/llm"
    output = (subprocess.check_output(command, shell=True, text=True)).split()
    output.append("-")
    return output

def aws_files():
    pass
def gcp_files():
    pass
def mysql_files():
    pass
def postgres_files():
    pass
# Create a list of dictionaries with image data and options
params = {
    "local": "-",
    "aws": "-",
    "gcp": "-",
    "mysql": "-",
    "postgres":"-"
}
if 'input_changed' not in st.session_state:
    st.session_state['input_changed'] = False

# Function to update session state based on key
def update_param(key, value):
    st.session_state[key] = value
    st.session_state["input_changed"] = True

for key, default_value in params.items():
    if key not in st.session_state:
        st.session_state[key] = default_value
        
for key, attributes in {
    "local":{
        'path': '/home/heliya/llm_finetuning/custom_llm/logos/local.jpg',
        'caption': 'Local',
        'options': local_files()
    },
    "aws":{
        'path': '/home/heliya/llm_finetuning/custom_llm/logos/aws.png',
        'caption': 'AWS',
        'options': ["-"] + [section for section in section_names if "aws" in section]
    },
    "gcp" :{
        'path': '/home/heliya/llm_finetuning/custom_llm/logos/googlestorage.png',
        'caption': 'Google Storage',
        'options': ["-"] + [section for section in section_names if "gcp" in section]
    },
    "mysql":{
        'path': '/home/heliya/llm_finetuning/custom_llm/logos/mysql.png',
        'caption': 'MySQL',
        'options': ["-"] + [section for section in section_names if "sql" in section and secrets[section]["db_type"] == "MySQL"]
    },
    "postgres": {
        'path': '/home/heliya/llm_finetuning/custom_llm/logos/postgres.png',
        'caption': 'Postgres',
        'options': ["-"] + [section for section in section_names if "sql" in section and secrets[section].get("db_type") == "PostgreSQL"]
    },
}.items():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(attributes['path'], use_column_width=False, width=160)    
    with col2:
        selected_option = st.selectbox(
            '',
            attributes['options'],
            key=key + "_input",
            index=attributes['options'].index(st.session_state[key])
        )
        
        # Update the selected option in the session state
        update_param(key, selected_option)
        
st.write(selected_option) 
