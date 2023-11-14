import streamlit as st

st.markdown("# Make Inference")

model_name = st.sidebar.selectbox(
    "Select a model to download",
    ('m1', 'm2', 'm3','custom',"None")
)

if model_name == "custom":
    model_name = st.text_input("Custom model name", key="custom_model_input")

load_model_name = st.sidebar.selectbox(
    "Load a model to use",
    ('m1', 'm2', 'm3')
)
import streamlit as st

txt = st.text_area(
    "Text to analyze",
    "",
    )

st.write(f'You wrote {len(txt)} characters.')

send, right_column = st.columns(2)

# Add a 'Train' button in the first column
if send.button('Send'):
    # Add a placeholder for iterations and progress bar in the second column

    # Display a message when training is done
    send.write("Answer")
    message = st.chat_message("assistant")
    message.write("Hello based on the text provided: ....")



