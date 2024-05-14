import streamlit as st
import requests
from streamlit_chat import message

st.set_page_config(page_title="Competition Results Chat Bot", layout="centered")

st.title("Competition Results Chat Bot")

# Initialize session state for storing chat history and file upload status
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "followup_question" not in st.session_state:
    st.session_state.followup_question = ""

# Function to send message to the server and get a response
def get_server_response(endpoint, payload=None):
    url = f"http://localhost:8000/{endpoint}/"
    try:
        if endpoint == "ask_followup":
            response = requests.post(url, json=payload)
        else:
            response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Sidebar for file upload
with st.sidebar:
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
                        st.session_state.uploaded = True
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please upload a .txt file.")

# Center chat area
if st.session_state.uploaded:
    st.markdown("<h2 style='text-align: center;'>Competition Results Chat</h2>", unsafe_allow_html=True)

    # Chat box container
    st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
            background-color: #f9f9f9;
            height: 500px;
        }
        .chat-box {
            flex-grow: 1;
            overflow-y: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        # Display chat messages inside chat box
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for role, message_text in st.session_state.messages:
            if role == "user":
                message(message_text, is_user=True)
            else:
                message(message_text, is_user=False)
        st.markdown('</div>', unsafe_allow_html=True)

        # Follow-up question input at the bottom of the chat area
        st.text_input("Ask a follow-up question:", key="followup_input", value=st.session_state.followup_question, placeholder="Ask another question...", label_visibility="collapsed")

        if st.button("Send Follow-Up Question"):
            if st.session_state.followup_question:
                st.session_state.messages.append(("user", st.session_state.followup_question))
                with st.spinner('Retrieving answer...'):
                    response = get_server_response("ask_followup", {"question": st.session_state.followup_question})
                    if isinstance(response, str) and response.startswith("Error"):
                        st.session_state.messages.append(("bot", response))
                    else:
                        st.session_state.messages.append(("bot", response))
                # Clear follow-up input after sending
                st.session_state.followup_question = ""
            else:
                st.error("Please enter a question.")

        # Query section with buttons for initial queries
        st.write("### Query Competition Results")
        placement = st.text_input("Enter the placement:", key="placement_input")

        col1, col2 = st.columns(2)

        if col1.button("Get Department"):
            if placement:
                with st.spinner('Retrieving department...'):
                    response = get_server_response(f"get_department/{placement}")
                    st.session_state.messages.append(("user", f"What is the department with placement {placement}?"))
                    if isinstance(response, str) and response.startswith("Error"):
                        st.session_state.messages.append(("bot", response))
                    else:
                        st.session_state.messages.append(("bot", response))
            else:
                st.error("Please enter a placement.")

        if col2.button("Get Employee"):
            if placement:
                with st.spinner('Retrieving employee...'):
                    response = get_server_response(f"get_employee/{placement}")
                    st.session_state.messages.append(("user", f"Who is the employee with placement {placement}?"))
                    if isinstance(response, str) and response.startswith("Error"):
                        st.session_state.messages.append(("bot", response))
                    else:
                        st.session_state.messages.append(("bot", response))
            else:
                st.error("Please enter a placement.")

        st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

else:
    st.write("Please upload a file to start querying the competition results.")
