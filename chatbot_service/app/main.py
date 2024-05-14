import streamlit as st
import requests

st.set_page_config(page_title="Competition Results Uploader", layout="centered")

st.title("Competition Results Uploader")

# File upload section
st.header("Upload a .txt file")
uploaded_file = st.file_uploader("Choose a .txt file", type="txt")

if uploaded_file is not None:
    if uploaded_file.name.endswith('.txt'):
        try:
            # Read the file content
            file_content = uploaded_file.read()
            
            # Define the files dictionary for the multipart/form-data request
            files = {'file': (uploaded_file.name, file_content, 'text/plain')}
            
            with st.spinner('Uploading file...'):
                response = requests.post("http://localhost:8000/upload/", files=files)
                if response.status_code == 200:
                    st.success("File uploaded and processed successfully")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please upload a .txt file.")

# Query section
st.header("Query Competition Results")
placement = st.text_input("Enter the placement:")

col1, col2 = st.columns(2)

with col1:
    if st.button("Get Department"):
        if placement:
            with st.spinner('Retrieving department...'):
                response = requests.get(f"http://localhost:8000/get_department/{placement}")
                if response.status_code == 200:
                    st.write("Department:", response.json())
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        else:
            st.error("Please enter a placement.")

with col2:
    if st.button("Get Employee"):
        if placement:
            with st.spinner('Retrieving employee...'):
                response = requests.get(f"http://localhost:8000/get_employee/{placement}")
                if response.status_code == 200:
                    st.write("Employee:", response.json())
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        else:
            st.error("Please enter a placement.")
