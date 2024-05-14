# Mlytica AI Assistant

## Product Demo

[![Watch the video](https://via.placeholder.com/150)](https://drive.google.com/file/d/1dny0Z7wjFq9n0f2mO0PAQUaA5WLuhCvm/preview)

## Overview

Mlytica AI Assistant is an advanced document-based question-answering application. It leverages Retrieval-Augmented Generation (RAG) and the FastAPI framework to provide precise and contextually appropriate answers to user queries based on uploaded documents.

## Features

- **User-Friendly Interface**: Intuitive interaction through a clean and straightforward interface built using streamlit.
- **Document Upload**: Easily upload documents for information retrieval.
- **Question-Answering**: Ask questions related to the document's content and receive precise answers.
- **Advanced Retrieval Techniques**: Uses RAG to retrieve relevant context from documents.

## Technical Description

### Retrieval-Augmented Generation (RAG)
RAG retrieves relevant context from the uploaded document to generate accurate and contextually appropriate answers for the user.

### FastAPI Framework
The backend of the app is built with FastAPI, ensuring fast performance and easy scalability.

### Additional Endpoints
Besides the main functionality, additional endpoints are integrated for uploading files and managing follow-up questions.

## Suggested Future Features

### Enhancements and New Capabilities
1. **Integration with LLM Function Calls**: Future versions could incorporate function calls within large language models to perform complex tasks directly from the user's commands, extending the app’s utility. This can be easily implemented using libraries like Langchain or LlamaIndex.

2. **Multi-Agent System**: Implementing a multi-agent system using CrewAI or LangGraph could address complex, multi-hop questions and facilitate step-by-step planning and reflective processes. This approach improves the quality of results by utilizing iterative workflows and processes (basically LLMs checking each other's answers).

These features could differentiate Mlytica's AI Assistant from other "AI applications" that merely call the OpenAI API.

## How to Run the App

### Prerequisites

- Ensure you have Python installed on your machine.
- Install required dependencies by running `pip install -r requirements.txt`.

### Steps to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/achrefbenammar404/mlytica_coding_task.git
   cd mlytica_coding_task
   ```

2. **Start the API Service**
   Navigate to the API service directory and run the FastAPI app using Uvicorn:
   ```bash
   cd api_service/app
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Start the Client Side**
   Open a new terminal, navigate to the client service directory, and run the Streamlit app:
   ```bash
   cd chatbot_service/app
   streamlit run main.py
   ```

### Usage

1. **Starting the App**: Launch the app through its URL or locally. You'll be greeted by a user-friendly interface designed for intuitive interaction.

2. **Uploading Documents**: To begin, upload a document from which you want the app to retrieve information. Click on the 'Upload Document' button and select the file from your device.

3. **Asking Questions**: Once the document is uploaded, you can start asking questions related to the document's content. Enter your question in the provided text field and submit it by clicking the 'Ask' button.

4. **Receiving Answers**: The app uses advanced retrieval techniques to provide precise answers. After submitting your question, the answer will appear on the same page, allowing you to ask follow-up questions if necessary.
