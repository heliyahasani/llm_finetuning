import streamlit as st
import toml

st.markdown("# Load Credentials 🔑")

# Use the password input field
hugging_face_token = st.text_input("Hugging Face Token", type='password', key="hugging_face_token")
openai_token = st.text_input("OpenAI Token", type='password', key="openai_token")


# Function to update the secrets file
def update_secrets_file(secrets_data):
    try:
        with open('secrets.toml', 'r') as file:
            secrets = toml.load(file)
    except FileNotFoundError:
        secrets = {}

    secrets.update(secrets_data)

    with open('secrets.toml', 'w') as file:
        toml.dump(secrets, file)

# Creating a form for SQL connection details
with st.form("sql_connection_form"):
    st.write("Please enter your SQL database connection details:")
    db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQLite"])
    host = st.text_input("Host")
    port = st.text_input("Port")  # Using an integer format
    database = st.text_input("Database Name")
    user = st.text_input("User")
    password = st.text_input("Password", type="password")

    # Form submission button
    submitted = st.form_submit_button("Submit")



    # Prepare the data to be saved
    secrets_data = {
        "hugging_face_token": hugging_face_token,
        "openai_token":openai_token,
        "db_type": db_type,
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password  # Be cautious with storing passwords in plain text
    }

#Initialize states
state_names = [hugging_face_token,openai_token,db_type,host,port,database,]


# Update the secrets file
# update_secrets_file(secrets_data)
