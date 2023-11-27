import streamlit as st

st.markdown("# Make Inference")

st.sidebar.title("Choose Model to Download")
selected_model = st.sidebar.selectbox(
    "Select a model to download",
    ('meta-llama/Llama-2-7b-chat-hf', 'adept/fuyu-8b', '01-ai/Yi-34B','mistralai/Mistral-7B-v0.1','Custom','-')
)

if selected_model == "Custom":
    custom_model = st.text_input("Custom model name", key="custom_model_input")
    st.session_state['model_name'] = custom_model
else:
    st.session_state['model_name'] = selected_model

st.sidebar.title("Choose Model to Use")
load_model_name = st.sidebar.selectbox(
    "Choose a model to use",
    ('meta-llama/Llama-2-7b-chat-hf',)
)
if selected_model == "-":
    st.session_state['load_model_name'] = load_model_name


txt = st.text_area(
    "Text to analyze",
    "",
    )
st.write(f'You wrote {len(txt)} characters.')

system_prompt = st.text_area(
    "System prompt (Optional)",
    "",
    )


send, right_column = st.columns(2)

# Add a 'Train' button in the first column
if send.button('Send'):
    # Add a placeholder for iterations and progress bar in the second column

    # Display a message when training is done
    send.write("Answer")
    message = st.chat_message("assistant")
    message.write("Hello based on the text provided: ....")



####Sidebar######
st.sidebar.title("Choose Input")
loaded_inputs = st.sidebar.selectbox("Select Loaded Data", ('summary.csv', 'book.txt'))
st.session_state['choosen_input'] = loaded_inputs
