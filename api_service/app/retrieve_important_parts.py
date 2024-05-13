import os
import json
import logging
import requests
from langchain_chroma import Chroma
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InformationExtractor:
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="kymadaembedding",
        azure_endpoint="https://frfraoaikymchat0005.openai.azure.com/",
        api_key="cd8a4aa317b9451b91d4e991df77b8ed",
        api_version="2023-12-01-preview"
    )

    def __init__(self, k=15):
        self.documents_paths = []
        self.retriever = None
        self.vectorstore = None
        self.k = k
        self.running = False
        self.indexed = []

    def extract_relevant_info_rag(self, task : str ) -> str :
        if self.retriever is None or self.vectorstore is None:
            logger.warning("No documents uploaded for reading. Please upload files first.")
            return "No documents uploaded to be read. You or your co-worker (information provider) need to use the upload user file tool to get relevant files from the user."

        try:
            list_documents = self.retriever.get_relevant_documents(task)
            return '----------------------------\n\n'.join([f"chunk Number {i}: {doc.page_content}" for i, doc in enumerate(list_documents)])
        except Exception as e:
            logger.error(f"Error retrieving relevant documents: {e}")
            return "Error occurred while retrieving documents."

    def add_document(self, document_path : str ) -> None :
        self.running = True
        try:
            self.documents_paths.append(document_path)
            loader = TextLoader(document_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
            splits = text_splitter.split_documents(docs)
            logger.info(f"Loading document from path: {document_path}")

            if self.vectorstore is None:
                self.vectorstore = Chroma.from_documents(documents=splits, embedding=InformationExtractor.embeddings)
            else:
                self.vectorstore.add_documents(docs)

            self.retriever = self.vectorstore.as_retriever(search_kwargs={'k': self.k})
            self.indexed.append(document_path)
            logger.info(f"upload of file {document_path} successful")
        except Exception as e:
            logger.error(f"Error adding document '{document_path}': {e}")
        finally:
            self.running = False




