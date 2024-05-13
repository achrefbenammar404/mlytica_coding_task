from fastapi import FastAPI, HTTPException
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from retrieve_important_parts import InformationExtractor 
from time import sleep 


app = FastAPI()
path = "competition_results.txt"
information_extractor = InformationExtractor()
information_extractor.add_document(document_path=path)
#data_manager = DataManager()

llm = AzureChatOpenAI(
            openai_api_key="cd8a4aa317b9451b91d4e991df77b8ed",
            azure_endpoint="https://frfraoaikymchat0005.openai.azure.com/",
            azure_deployment="kymgpt35",
            api_version="2023-12-01-preview",
            temperature=0
)

messages = []


@app.get("/get_department/{placement}")
def get_department(placement: str)->str:
    while(information_extractor.running ):
        sleep(1)
    chain = create_langchain_chain()
    context , question  = get_context_question("department" , placement=placement)
    return chain.invoke({"question" : question  , 'chunks' : context})


@app.get("/get_employee/{placement}")
def get_employee(placement: str)->str:
    while(information_extractor.running ):
        sleep(1)
    chain = create_langchain_chain()
    context , question  = get_context_question("employee" , placement=placement)
    return "employee"
    return chain.invoke({"question" : question  , 'chunks' : context})



def create_langchain_chain () : 
    prompt_message = (
        """
        you are an AI assistant that can extract information from context extracted from various documents. 
        you will be given a context that will contain information relevant to the question you are being tasked. Your task is to answer the question based only on the snippets of the documnt given to you, if you don't find the answer in the snippets you can repky by "answer not found in the snippets given to me".
        this is the question given to you : {question}
        these are the snippets based on whoch you will answer the question : {chunks}.
        Your answer should be entirely based on the snippets given to you. 
    """)
    prompt = ChatPromptTemplate.from_template(prompt_message)
    
    llm = AzureChatOpenAI(
        openai_api_key="cd8a4aa317b9451b91d4e991df77b8ed",
        azure_endpoint="https://frfraoaikymchat0005.openai.azure.com/",
        azure_deployment="kymgpt35",
        api_version="2023-12-01-preview",
        temperature=0
    )
    
    parser = StrOutputParser()
    
    return {"chunks": RunnablePassthrough(), "question": RunnablePassthrough() } | prompt | llm |parser  


def get_context_question(element_questioned : str , placement : int  ) -> str : 
    if (element_questioned == "department") : 
        question = f"What is the {element_questioned} with the placement : {placement} in this competition?"
    elif (element_questioned == "employee") : 
        question = f"Who is the {element_questioned} with the placement {placement} in this competition?"

    context = information_extractor.extract_relevant_info_rag(task=question)
    return context , question