import streamlit as st
import time

st.markdown("# Training Hyperparameter Configuration🎈")

# Initialize session state variables
params = {
    "max_sequence_length": 100,
    "micro_batch_size": 1,
    "epochs": 1,
    "learning_rate": 0.00001,
    "lora_r":1,
    "lora_alpha":1,
    "lora_dropout":0.0
}
for key, default_value in params.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Function to update session state based on key
def update_param(key, value):
    st.session_state[key] = value

# Create sliders and inputs
for key, attributes in {
    "max_sequence_length": {"min": 1, "max": 5096, "step": 1, "format": "%d"},
    "micro_batch_size": {"min": 1, "max": 100, "step": 1, "format": "%d"},
    "epochs": {"min": 1, "max": 1000, "step": 1, "format": "%d"},
    "learning_rate": {"min": 0.0, "max": 1.0, "step": 0.00001, "format": "%.5f"},
    "lora_r":{"min": 1, "max": 64, "step": 1, "format": "%d"},
    "lora_alpha":{"min": 1, "max": 128, "step": 1, "format": "%d"},
    "lora_dropout":{"min": 0.0, "max": 1.0, "step": 0.01, "format": "%.2f"}
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



####Sidebar######
# Create the main sidebar
st.sidebar.title("Model & Tokenizer")
# Add a selectbox to the sidebar:
model_name = st.sidebar.selectbox(
    "Select a Model",
    ('m1', 'm2', 'm3','custom')
)
if model_name == "custom":
    model_name = st.text_input("Custom model name", key="custom_model_input")


tokenizer_name = st.sidebar.selectbox(
    "Select a Tokenizer",
    ('t1', 't2', 't3','Custom')
)
if tokenizer_name == "Custom":
    tokenizer_name = st.text_input("Custom tokenizer name", key="custom_tokenizer_input")

train, right_column = st.columns(2)

# Add a 'Train' button in the first column
if train.button('Train'):
    train.write('Starting to train the model...')

    # Add a placeholder for iterations and progress bar in the second column
    latest_iteration = right_column.empty()
    bar = right_column.progress(0)

    # Simulate a training loop
    for i in range(100):
        # Update the progress bar and iteration text with each iteration
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.100)

    # Display a message when training is done
    train.write("...and now we're done!")
