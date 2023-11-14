import streamlit as st
import pandas as pd
from io import StringIO
from streamlit.connections import SQLConnection

st.markdown("# Load or Connect Your Data")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    file_name = uploaded_file.name
    extension = file_name.split('.')[-1]

    st.write(f"The uploaded file is a .{extension} file.")
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    st.write(string_data)


