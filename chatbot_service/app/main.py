import asyncio
import aiohttp
import streamlit as st

st.set_page_config(page_title="Competition Results Chat Bot", layout="centered")

st.title("Competition Results Chat Bot")

# Initialize session state for storing chat history and file upload status
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

# Helper function to add messages to the session state
def add_message(role, message_text):
    st.session_state.messages.append((role, message_text))

# Asynchronous function to send message to the server and get a response
async def get_server_response(endpoint, payload=None, files=None):
    url = f"http://localhost:8000/{endpoint}/"
    try:
        async with aiohttp.ClientSession() as session:
            if payload:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    return await response.json()
            elif files:
                async with session.post(url, data=files) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
    except aiohttp.ClientError as e:
        st.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"

# Sidebar for file upload, optional placement input, and querying results
with st.sidebar:
    st.header("Upload a .txt file")
    uploaded_file = st.file_uploader("Choose a .txt file", type="txt")

    placement = st.text_input("Enter the placement (optional):")

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.txt'):
            try:
                with st.spinner('Uploading file...'):
                    # Read the file content
                    file_content = uploaded_file.getvalue()

                    # Prepare files for multipart form data
                    files = aiohttp.FormData()
                    files.add_field('file', file_content, filename=uploaded_file.name, content_type='text/plain')

                    # Send file to the server
                    response = asyncio.run(get_server_response("upload", files=files))
                    if response.get("status") == "File uploaded and processed successfully":
                        st.success("File uploaded and processed successfully")
                        st.session_state.uploaded = True
                    else:
                        st.error(f"Error: {response.get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please upload a .txt file.")

    if st.session_state.uploaded:
        st.markdown("### Query Competition Results")
        
        col1, col2 = st.columns(2)

        if col1.button("Get Department"):
            if placement:
                add_message("user", f"What is the department with placement {placement}?")
                with st.spinner('Retrieving department...'):
                    response = asyncio.run(get_server_response(f"get_department/{placement}"))
                    if isinstance(response, str) and response.startswith("Error"):
                        add_message("assistant", response)
                    else:
                        add_message("assistant", response)
            else:
                st.error("Please enter a placement.")

        if col2.button("Get Employee"):
            if placement:
                add_message("user", f"Who is the employee with placement {placement}?")
                with st.spinner('Retrieving employee...'):
                    response = asyncio.run(get_server_response(f"get_employee/{placement}"))
                    if isinstance(response, str) and response.startswith("Error"):
                        add_message("assistant", response)
                    else:
                        add_message("assistant", response)
            else:
                st.error("Please enter a placement.")

# Center chat area
if st.session_state.uploaded:
    st.markdown("## Chat with AI Assistant")

    # Display chat messages using st.chat_message
    for i, (role, message_text) in enumerate(st.session_state.messages):
        if role == "user":
            with st.chat_message("user", avatar=":material/person:") :
                st.markdown(message_text)
        else:
            with st.chat_message("assistant", avatar=":material/robot:") :
                st.markdown(message_text)

    # Form to handle follow-up questions
    with st.form(key="followup_form"):
        followup_input = st.text_input("Ask a follow-up question...", key="followup_input")
        submit_button = st.form_submit_button(label="Send")

        if submit_button and followup_input:
            add_message("user", followup_input)

            conversation_history = [f"{role}: {message_text}" for role, message_text in st.session_state.messages]

            with st.spinner('Retrieving answer...'):
                payload = {"question": followup_input, "conversation_history": conversation_history}
                response = asyncio.run(get_server_response("ask_followup_with_context", payload=payload))
                if isinstance(response, str) and response.startswith("Error"):
                    add_message("assistant", response)
                else:
                    add_message("assistant", response)

            # Clear the form input by rerunning the script
            st.experimental_rerun()
