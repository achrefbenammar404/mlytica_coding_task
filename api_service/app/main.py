from fastapi import FastAPI, HTTPException, UploadFile, File
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from retrieve_important_parts import InformationExtractor
from time import sleep
import os
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
# Define a Pydantic model for the follow-up question request
class FollowUpRequest(BaseModel):
    question: str

# Load environment variables from .env file
load_dotenv()

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create FastAPI app instance
app = FastAPI()

# Retrieve sensitive data from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_CHAT")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT_CHAT")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_CHAT")

information_extractor = InformationExtractor()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Check if the uploaded file is a .txt file
        file_ext = os.path.splitext(file.filename)[1]
        if file_ext.lower() != '.txt':
            raise HTTPException(status_code=415, detail="Unsupported file type, only .txt files are accepted")

        # Read and decode file contents
        contents = await file.read()
        contents = contents.decode("utf-8")

        # Save contents to a temporary file - this is needed if add_document requires a file path
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(contents)

        # Update the document in InformationExtractor
        information_extractor.add_document(document_path=temp_file_path)

        # Optionally, delete the temp file if no longer needed
        os.remove(temp_file_path)

        return {"filename": file.filename, "status": "File uploaded and processed successfully"}
    except HTTPException as http_exc:
        # Reraise the caught HTTPException
        raise http_exc
    except Exception as e:
        logging.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Initialize language model
llm = AzureChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    azure_deployment=AZURE_DEPLOYMENT,
    api_version="2023-12-01-preview",
    temperature=0
)

@app.get("/get_department/{placement}")
def get_department(placement: str) -> str:
    """
    Retrieve the department associated with a specific placement from competition results.
    """
    try:
        while information_extractor.running:
            sleep(1)
        chain = create_langchain_chain()
        context, question = get_context_question("department", placement=placement)
        return chain.invoke({"question": question, 'chunks': context})
    except Exception as e:
        logging.error(f"Error in get_department: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/get_employee/{placement}")
def get_employee(placement: str) -> str:
    """
    Retrieve the employee associated with a specific placement from competition results.
    """
    try:
        while information_extractor.running:
            sleep(1)
        chain = create_langchain_chain()
        context, question = get_context_question("employee", placement=placement)
        return chain.invoke({"question": question, 'chunks': context})
    except Exception as e:
        logging.error(f"Error in get_employee: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/ask_followup/")
async def ask_followup(request: FollowUpRequest):
    """
    Handle follow-up questions based on previously processed data.
    """
    try:
        context = information_extractor.extract_relevant_info_rag(task=request.question)
        chain = create_langchain_chain()
        return chain.invoke({"question": request.question, 'chunks': context})
    except Exception as e:
        logging.error(f"Error in ask_followup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    



def create_langchain_chain():
    """
    Create a language processing chain to handle incoming queries and context.
    """
    prompt_message = (
        """
        You are an AI assistant that can extract information from context extracted from various documents. 
        You will be given a context that will contain information relevant to the question you are being tasked. Your task is to answer the question based only on the snippets of the document given to you, if you don't find the answer in the snippets you can reply by "answer not found in the snippets given to me".
        This is the question given to you: {question}
        These are the snippets based on which you will answer the question: {chunks}.
        Your answer should be entirely based on the snippets given to you. 
        """
    )
    prompt = ChatPromptTemplate.from_template(prompt_message)
    
    llm = AzureChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        azure_deployment=AZURE_DEPLOYMENT,
        api_version="2023-12-01-preview",
        temperature=0
    )
    
    parser = StrOutputParser()
    
    return RunnablePassthrough() | prompt | llm | parser

def get_context_question(element_questioned: str, placement: int) -> (str, str):
    """
    Generate the context and question for the given element and placement.
    """
    if element_questioned == "department":
        question = f"What is the {element_questioned} with the placement: {placement} in this competition?"
    elif element_questioned == "employee":
        question = f"Who is the {element_questioned} with the placement {placement} in this competition?"
    context = information_extractor.extract_relevant_info_rag(task=question)
    return context, question
