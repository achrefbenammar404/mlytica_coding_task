from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from retrieve_important_parts import InformationExtractor
import os
import logging
from dotenv import load_dotenv
import asyncio

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_CHAT")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT_CHAT")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_CHAT")

information_extractor = InformationExtractor(k = 15)

class FollowUpRequest(BaseModel):
    question: str
    conversation_history: List[str]

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=415, detail="Unsupported file type, only .txt files are accepted")

        contents = await file.read()
        contents = contents.decode("utf-8")

        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(contents)

        information_extractor.add_document(temp_file_path)

        os.remove(temp_file_path)

        return {"filename": file.filename, "status": "File uploaded and processed successfully"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

llm = AzureChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    azure_deployment=AZURE_DEPLOYMENT,
    api_version="2023-12-01-preview",
    temperature=0.5
)

@app.get("/get_department/{placement}")
async def get_department(placement: str) -> str:
    return await process_request("department", placement)

@app.get("/get_employee/{placement}")
async def get_employee(placement: str) -> str:
    return await process_request("employee", placement)

@app.post("/ask_followup_with_context")
async def ask_followup_with_context(request: FollowUpRequest) -> str:
    try:
        chain = create_langchain_chain()
        context = "\n".join(request.conversation_history) + f"\nUser: {request.question}"
        relevant_context = information_extractor.extract_relevant_info_rag(task=request.question + f" {request.conversation_history}")
        return chain.invoke({"question": request.question, 'chunks': relevant_context})
    except Exception as e:
        logging.error(f"Error in ask_followup_with_context: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    

async def process_request(element_questioned: str, placement: str) -> str:
    try:
        while information_extractor.running:
            await asyncio.sleep(1)
        chain = create_langchain_chain()
        context, question = get_context_question(element_questioned, placement)
        return chain.invoke({"question": question, 'chunks': context})
    except Exception as e:
        logging.error(f"Error in process_request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def create_langchain_chain():
    prompt_message = (
        """
        You are a sassy and energetic AI assistant that has information from context extracted from various documents. 
        You will be given a context that will contain information relevant to the question you are being tasked. Your task is to answer the question based only on the snippets of the document given to you, if you don't find the answer in the snippets you can reply by being sassy and funny.
        This is the question given to you: {question}
        These are the snippets based on which you will answer the question: {chunks}.
        """
    )
    prompt = ChatPromptTemplate.from_template(prompt_message)
    parser = StrOutputParser()
    return RunnablePassthrough() | prompt | llm | parser

def get_context_question(element_questioned: str, placement: str) -> (str, str):
    if element_questioned == "department":
        question = f"What is the {element_questioned} with the placement: {placement} in this competition?"
    elif element_questioned == "employee":
        question = f"Who is the {element_questioned} with the placement {placement} in this competition?"
    context = information_extractor.extract_relevant_info_rag(task=question)
    return context, question
