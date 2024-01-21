import shutil
import streamlit as st
import time
import json
from train.train_model import ModelTrainer

from datasets import Dataset
from train.hugging_face_api_request import ApiRequest
from load_connect_data.data_loading import connect_postgres, connect_mysql, connect_bigquery,connect_aws,handle_local_files,connect_bucket
from load_connect_data.storage import  upload_to_aws,upload_object_to_bucket
import toml
import gc
import torch
import os
torch.cuda.empty_cache()
gc.collect()
    
st.markdown("# Training Hyperparameter Configuration🎈")
# Load the TOML file
with open('secrets.toml', 'r') as file:
    secrets = toml.load(file)
section_names = secrets.keys()

load_data = st.selectbox("Where to load data?", ["Local", "AWS", "GCP BIGQUERY","GCP BUCKETS", "Postgres", "MySQL"])
if load_data == "Local":
    df = handle_local_files()
    if df is not None:
        st.session_state['choosen_input'] = Dataset.from_pandas(df)    
    
elif load_data == "AWS":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "aws" in section], key="aws_configuration")
    df = connect_aws(secrets, configuration)
    if df is not None:
        st.session_state['choosen_input'] = Dataset.from_pandas(df)  
elif load_data == "GCP BIGQUERY":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "gcp" in section and secrets[section].get("type") == "BigQuery"], key="gcp_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        df=connect_bigquery(secrets, configuration, query=query)
        if df is not None:
            st.session_state['choosen_input'] = Dataset.from_pandas(df)    
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "GCP BUCKETS":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "gcp" in section and secrets[section].get("type") == "Buckets"], key="gcp_configuration")
    if configuration in secrets:
        df=connect_bucket(secrets, configuration)
        if df is not None:
            st.session_state['choosen_input'] = Dataset.from_pandas(df)    
    else:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "Postgres":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "sql" in section and secrets[section].get("db_type") == "PostgreSQL"], key="postgres_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        df=connect_postgres(secrets, configuration, query=query)
        if df is not None:
            st.session_state['choosen_input'] = Dataset.from_pandas(df)    
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "MySQL":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "sql" in section and secrets[section]["db_type"] == "MySQL"], key="mysql_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        df = connect_mysql(secrets, configuration, query=query)
        if df is not None:
            st.session_state['choosen_input'] = Dataset.from_pandas(df)    
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")

# Initialize session state variables
params = {
    "max_sequence_length": 100,
    "micro_batch_size": 1,
    "epochs": 1,
    "learning_rate": 0.00001,
    "lora_r":1,
    "lora_alpha":1,
    "lora_dropout":0.0,
    "gradient_accumulation_steps":1,
    "logging_steps":5
}
for key, default_value in params.items():
    if key not in st.session_state:
        st.session_state[key] = default_value
        
# Initialize session state for model and tokenizer
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = None # Default model
if 'tokenizer_name' not in st.session_state:
    st.session_state['tokenizer_name'] = None # Default tokenizer
if 'quantazation' not in st.session_state:
    st.session_state['quantazation'] = None # Default quantazation

if 'input_changed' not in st.session_state:
    st.session_state['input_changed'] = False

# Function to update session state based on key
def update_param(key, value):
    st.session_state[key] = value
    st.session_state["input_changed"] = True

# Create sliders and inputs
for key, attributes in {
    "max_sequence_length": {"min": 1, "max": 5096, "step": 1, "format": "%d"},
    "micro_batch_size": {"min": 1, "max": 100, "step": 1, "format": "%d"},
    "epochs": {"min": 1, "max": 1000, "step": 1, "format": "%d"},
    "learning_rate": {"min": 0.0, "max": 1.0, "step": 0.00001, "format": "%.5f"},
    "lora_r":{"min": 1, "max": 64, "step": 1, "format": "%d"},
    "lora_alpha":{"min": 1, "max": 128, "step": 1, "format": "%d"},
    "lora_dropout":{"min": 0.0, "max": 1.0, "step": 0.01, "format": "%.2f"},
    "gradient_accumulation_steps":{"min": 0, "max": 1000, "step": 1, "format": "%d"},
    "logging_steps":{"min": 0, "max": 1000, "step": 5, "format": "%d"}
}.items():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.slider(
            key.replace('_', ' ').title(),
            min_value=attributes["min"],
            max_value=attributes["max"],
            value=st.session_state[key],
            step=attributes["step"],
            format=attributes["format"],
            key=key+"_slider"
        )
    with col2:
        st.number_input(
            '',
            min_value=attributes["min"],
            max_value=attributes["max"],
            value=st.session_state[key],
            step=attributes["step"],
            format=attributes["format"],
            on_change=update_param,
            args=(key, st.session_state[key+"_slider"]),
            key=key+"_input"
        )

# Logic to handle changes
if 'input_changed' in st.session_state and st.session_state['input_changed']:
    # Reset the flag
    st.session_state['input_changed'] = False


####Sidebar######
# Create the main sidebar
st.sidebar.title("Model & Tokenizer")
selected_model = st.sidebar.selectbox("Select a Model", ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B','mistralai/Mixtral-8x7B-Instruct-v0.1','Custom'))
# Add a selectbox to the sidebar:
if selected_model == "Custom":
    # Custom model input
    custom_model = st.sidebar.text_input("Custom model name", key="custom_model_input")
    st.session_state['model_name'] = custom_model
else:
    st.session_state['model_name'] = selected_model

# Tokenizer selection
selected_tokenizer = st.sidebar.selectbox("Select a Tokenizer", ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B','mistralai/Mixtral-8x7B-Instruct-v0.1','Custom'))
if selected_tokenizer == "Custom":
    # Custom tokenizer input
    custom_tokenizer = st.sidebar.text_input("Custom tokenizer name", key="custom_tokenizer_input")
    st.session_state['tokenizer_name'] = custom_tokenizer
else:
    st.session_state['tokenizer_name'] = selected_tokenizer

# Quantazation selection
selected_quantazation = st.sidebar.selectbox("Quantazation", (None,'4-bit','8-bit'))
st.session_state['quantazation'] = selected_quantazation


## Trending models in Hugging Face
st.sidebar.title("Trending models in Hugging Face")
with st.sidebar:
    st.write(ApiRequest(st.session_state['model_name']).leader_models())


def write_config_to_file(config, filename="training_config.json"):
    try:
        with open(filename, 'w') as file:
            json.dump(config, file, indent=4)
        print("Config file written successfully.")  # Debug message
    except Exception as e:
        print(f"Error writing config file: {e}")  # Error message

store_data = st.selectbox("Where to store data?", ["Local", "AWS","GCP"])
if store_data == "Local":
    local_directory = "./tmp/results"
    # Check if the directory exists
    if not os.path.exists(local_directory):
        # Create the directory if it doesn't exist
        os.makedirs(local_directory)
        st.session_state['storage'] = store_data
    
    if st.button("Save to Local Storage"):
        try:
            shutil.copytree(local_directory, store_data)
            st.success(f"Files copied from '{local_directory}' to '{store_data}' successfully.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

elif store_data == "AWS":
    st.session_state['storage'] = store_data 
    upload_to_aws()
    
elif store_data == "GCP": #done
    st.session_state['storage'] = store_data
    upload_object_to_bucket(store_data)
    

          
def get_training_config():
    return {
        "max_sequence_length": st.session_state["max_sequence_length"],
        "micro_batch_size": st.session_state["micro_batch_size"],
        "epochs": st.session_state["epochs"],
        "learning_rate": st.session_state["learning_rate"],
        "lora_r": st.session_state["lora_r"],
        "lora_alpha": st.session_state["lora_alpha"],
        "lora_dropout": st.session_state["lora_dropout"],
        "model_name":st.session_state['model_name'],
        "tokenizer_name":st.session_state['tokenizer_name'],
        "quantazation":st.session_state['quantazation'] ,
        "gradient_accumulation_steps":st.session_state['gradient_accumulation_steps'],
        "logging_steps":st.session_state['logging_steps'],   
    }
   

train, right_column = st.columns(2)

# Add a 'Train' button in the first column
if train.button('Train'):
    config = get_training_config()
    write_config_to_file(config)
    request_model = ApiRequest(st.session_state['model_name']).check_availibility()
    request_tokenizer = ApiRequest(st.session_state['tokenizer_name']).check_availibility()
    
    st.write(request_model,st.session_state['model_name'])
    st.write(request_tokenizer,st.session_state['tokenizer_name'])
       
    if (request_model == 200 and request_tokenizer == 200):
        st.write("Model and tokenizer found successfuly")
        train.write('Starting to train the model...')
        trainer = ModelTrainer(
            training_config_path='/home/heliya/llm_finetuning/custom_llm/training_config.json',
            secrets_path='/home/heliya/llm_finetuning/custom_llm/secrets.toml',
            dataset_name=st.session_state.get('choosen_input', None),  # Use the dataset from the session state
            output_dir='./tmp/results'
        )
        trainer.train()
        trainer.model.save_pretrained('./tmp/results')

        
        # Display a message when training is done
        train.write("...and now we're done!")
        train.write("Please wait for saving your model and documents.")
        
    else:
        st.write("Model or tokenizer NOT found try again.")

