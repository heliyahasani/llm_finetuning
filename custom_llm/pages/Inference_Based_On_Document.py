import streamlit as st
from inference.vllm_api_request import SupportedModelsScraper
from load_connect_data.data_loading import connect_postgres,connect_aws, connect_mysql, connect_bigquery, handle_local_files,connect_bucket
import toml
from inference.inference import Model

st.markdown("# Make Inference Based on Data Input")
# Load the TOML file
with open('secrets.toml', 'r') as file:
    secrets = toml.load(file)
section_names = secrets.keys()

####Sidebar######

st.sidebar.title("Choose Model to Use")
selected_model = st.sidebar.selectbox(
    "Select a model to download",
    ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B','mistralai/Mistral-7B-v0.1','Custom','-')
)

if selected_model == '-':
    st.writre("Model conflict!") 
elif selected_model != '-':
    st.session_state['model_name'] = selected_model



## Trending models in Hugging Face
st.sidebar.title("Supported Models")
with st.sidebar:
    scraper = SupportedModelsScraper()
    scraper.scrape_data()
    st.write(scraper.get_data())

if selected_model == "Custom":
    custom_model = st.text_input("Custom model name", key="custom_model_input")
    st.session_state['model_name'] = custom_model
else:
    st.session_state['model_name'] = selected_model

load_data = st.selectbox("Where to load data?", ["Local", "AWS", "GCP BIGQUERY","GCP BUCKETS", "Postgres", "MySQL"])

if load_data == "Local":
    df = handle_local_files()

elif load_data == "AWS":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "aws" in section], key="aws_configuration")
    df = connect_aws(secrets, configuration)

elif load_data == "GCP BIGQUERY":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "gcp" in section and secrets[section].get("type") == "BigQuery"], key="gcp_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        df = connect_bigquery(secrets, configuration, query=query)

    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "GCP BUCKETS":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "gcp" in section and secrets[section].get("type") == "Buckets"], key="gcp_configuration")
    if configuration in secrets:
        df=connect_bucket(secrets, configuration)
    
    else:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "Postgres":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "sql" in section and secrets[section].get("db_type") == "PostgreSQL"], key="postgres_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        df=connect_postgres(secrets, configuration, query=query)
     
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")
elif load_data == "MySQL":
    configuration = st.selectbox("Which configuration would you like to use ?", [section for section in section_names if "sql" in section and secrets[section]["db_type"] == "MySQL"], key="mysql_configuration")
    query = st.text_input("Enter your query", key="query")
    run = st.button("Run", type="primary")
    if run and configuration in secrets:
        df =connect_mysql(secrets, configuration, query=query)
    elif run:
        st.error(f"Configuration '{configuration}' not found in secrets.")

system_prompt = st.text_area(
    "System prompt (Optional)",
    "",
    )

send, right_column = st.columns(2)
counter =0
# Add a 'Train' button in the first column
if send.button('Send'):
    message = st.chat_message("Inference based on document has started. Please wait it might take too long.")
    model = Model(st.session_state['model_name'])
    column1_list = df['text'].tolist()
    generated_text = model.generate(column1_list,system_prompt=system_prompt)

    message.write("Inference has finished. below you can see first 10 rows of the inference.")
    st.write(generated_text)
