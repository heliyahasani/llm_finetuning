from transformers import AutoModelForCausalLM, AutoTokenizer
import streamlit as st
from inference.inference import Model
from load_connect_data.get_fine_tuned_weights import upload_adapters_aws,upload_adapters_gcp,upload_adapters_local
import torch
from train.hugging_face_api_request import ApiRequest


torch.cuda.empty_cache()
adapter_model_path = '/home/heliya/llm_finetuning/custom_llm/tmp/results/adapter_model.bin'
st.session_state['model_name'] = 'meta-llama/Llama-2-7b-chat-hf'
# Title
st.markdown("# Make a Fine Tuned Model Inference")

# Sidebar
st.sidebar.title("Choose Model to Use")

# Select a model to download or use
selected_model = st.sidebar.selectbox(
    "Select a model to download",
    ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B', 'mistralai/Mistral-7B-v0.1', 'Custom', '-')
)
## Trending models in Hugging Face
st.sidebar.title("Trending models in Hugging Face")
with st.sidebar:
    st.write(ApiRequest(st.session_state['model_name']).leader_models())

# Check for model conflicts
if selected_model == '-':
    st.write("Model conflict!")

# Set the model name based on user selection
elif selected_model != '-':
    st.session_state['model_name'] = selected_model

# Supported Models in VLLM
st.sidebar.title("Supported Models")


# If the user selects "Custom," allow them to enter a custom model name
if selected_model == "Custom":
    custom_model = st.text_input("Custom model name", key="custom_model_input")
    st.session_state['model_name'] = custom_model
else:
    st.session_state['model_name'] = selected_model
    
    

get_data = st.selectbox("Where to get data?", ["Local", "AWS","GCP"])
if get_data=="Local":
    adapter_model_bin,adapter_model_json = upload_adapters_local()
elif get_data == "AWS":
    upload_adapters_aws()
else:
    upload_adapters_gcp()




# Function to load the model and adapter
def load_model_with_adapter(model_identifier, adapter_model_bin):
    # Load the pre-trained model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_identifier)
    tokenizer = AutoTokenizer.from_pretrained(model_identifier)

    # Load adapter model's state dict
    adapter_state_dict = torch.load(adapter_model_bin)

    # Update the pre-trained model's state dict with the adapter
    model_state_dict = model.state_dict()
    model_state_dict.update(adapter_state_dict)
    model.load_state_dict(model_state_dict)

# Function to generate text
def generate_text(model, tokenizer, prompt_text, max_length=240):
    # Encode input context
    input_ids = tokenizer.encode(prompt_text, return_tensors='pt')

    # Generate text
    model.eval()
    with torch.no_grad():
        outputs = model.generate(input_ids, max_length=max_length)

    # Decode and return generated text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text


# User specified model and tokenizer (replace 'gpt2' with any model from Hugging Face Model Hub)
model_identifier = selected_model

# Paths to your adapter
adapter_model_path = adapter_model_bin

# Load model with adapter
model, tokenizer = load_model_with_adapter(model_identifier, adapter_model_path)

# Text input
txt = st.text_area("Text", "")

# Generate text
generated_text = generate_text(model, tokenizer, txt)


# Display character count
st.write(f'You wrote {len(txt)} characters.')

# Send button and right column
send, right_column = st.columns(2)

# Handle user interaction when the "Send" button is clicked
if send.button('Send'):
    model = Model(st.session_state['model_name'])
    answer = model.generate(txt)

    # Display the answer
    send.write(generated_text)
    message = st.chat_message("assistant")
    message.write(answer)
