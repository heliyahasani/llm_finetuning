import streamlit as st
from inference.vllm_api_request import SupportedModelsScraper
from train.hugging_face_api_request import ApiRequest

st.markdown("# Make Inference Based on Data Input")

####Sidebar######

st.sidebar.title("Choose Model to Download")
selected_model = st.sidebar.selectbox(
    "Select a model to download",
    ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B','mistralai/Mistral-7B-v0.1','Custom','-')
)

st.sidebar.title("Choose Model to Use")
load_model_name = st.sidebar.selectbox(
    "Choose a model to use",
    ('meta-llama/Llama-2-7b-chat-hf','-')
)
if selected_model == '-' and load_model_name =='-':
    st.writre("Model conflict!") 
elif selected_model != '-':
    st.session_state['model_name'] = selected_model
elif load_model_name != '-':
    st.session_state['model_name'] = load_model_name

st.sidebar.title("Choose Input")
loaded_inputs = st.sidebar.selectbox("Select Loaded Data", ('summary.csv', 'book.txt'))
st.session_state['choosen_input'] = loaded_inputs

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
if selected_model == "-":
    st.session_state['load_model_name'] = load_model_name

system_prompt = st.text_area(
    "System prompt (Optional)",
    "",
    )

send, right_column = st.columns(2)

# Add a 'Train' button in the first column
if send.button('Send'):
    # Display a message when training is done
    send.write("Inference based on document has started. Please wait it might take too long.")
    ###### Some input algorithm
    message = st.chat_message("assistant")
    message.write("Inference has finished. below you can see first 10 rows of the inference.")


