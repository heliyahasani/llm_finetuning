import streamlit as st
from inference.inference import Model
from inference.vllm_api_request import SupportedModelsScraper
from train.hugging_face_api_request import ApiRequest

import torch
torch.cuda.empty_cache()

# Title
st.markdown("# Make Inference")

# Sidebar
st.sidebar.title("Choose Model to Download")

# Select a model to download
selected_model = st.sidebar.selectbox(
    "Select a model to download",
    ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B', 'mistralai/Mistral-7B-v0.1', 'Custom', '-')
)

st.sidebar.title("Choose Model to Use")

# Choose a model to use
load_model_name = st.sidebar.selectbox(
    "Choose a model to use",
    ('meta-llama/Llama-2-7b-chat-hf', '-')
)

# Check for model conflicts
if selected_model == '-' and load_model_name == '-':
    st.write("Model conflict!")

# Set the model name based on user selection
elif selected_model != '-':
    st.session_state['model_name'] = selected_model
elif load_model_name != '-':
    st.session_state['model_name'] = load_model_name

# Supported Models in VLLM
st.sidebar.title("Supported Models")

with st.sidebar:
    scraper = SupportedModelsScraper()
    scraper.scrape_data()
    st.write(scraper.get_data())

# If the user selects "Custom," allow them to enter a custom model name
if selected_model == "Custom":
    custom_model = st.text_input("Custom model name", key="custom_model_input")
    st.session_state['model_name'] = custom_model
else:
    st.session_state['model_name'] = selected_model

if selected_model == "-":
    st.session_state['model_name'] = load_model_name

# Text input
txt = st.text_area("Text", "")

# Display character count
st.write(f'You wrote {len(txt)} characters.')

# Send button and right column
send, right_column = st.columns(2)

# Handle user interaction when the "Send" button is clicked
if send.button('Send'):
    model = Model(st.session_state['model_name'])
    answer = model.generate(txt)

    # Display the answer
    send.write("Answer")
    message = st.chat_message("assistant")
    message.write(answer)
