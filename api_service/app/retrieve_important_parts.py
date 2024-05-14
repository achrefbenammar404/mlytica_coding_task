import os
import logging
from langchain_chroma import Chroma
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InformationExtractor:
    """
    A class dedicated to extracting and retrieving information from documents using vector embeddings.
    
    Attributes:
        embeddings (AzureOpenAIEmbeddings): Azure embeddings used for document vectorization.
        k (int): Number of relevant documents to retrieve.
        documents_paths (list): Paths to the documents loaded.
        retriever (Chroma): Document retriever based on vector embeddings.
        vectorstore (Chroma): Store of document vectors.
        running (bool): Flag indicating if document processing is ongoing.
        indexed (list): List of indexed document paths.
    """

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_DEPLOYMENT_EMBED"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT_EMBED"),
        api_key=os.getenv("AZURE_API_KEY_EMBED"),
        api_version="2023-12-01-preview"
    )

    def __init__(self, k=15):
        """
        Initializes the InformationExtractor with a specified number of documents to retrieve (k).
        """
        self.documents_paths = []
        self.retriever = None
        self.vectorstore = None
        self.k = k
        self.running = False
        self.indexed = []

    def extract_relevant_info_rag(self, task: str) -> str:
        """
        Retrieves relevant information based on the given task query from the loaded documents.
        
        Parameters:
            task (str): The query or task description to find relevant documents for.

        Returns:
            str: A concatenated string of the top relevant document chunks or an error message.
        """
        if self.retriever is None or self.vectorstore is None:
            logging.warning("Retrieval attempted before documents were properly uploaded and indexed.")
            return "No documents uploaded to be read. You or your co-worker (information provider) need to use the upload user file tool to get relevant files from the user."

        try:
            list_documents = self.retriever.get_relevant_documents(task)
            return '----------------------------\n\n'.join([f"Chunk Number {i}: {doc.page_content}" for i, doc in enumerate(list_documents)])
        except Exception as e:
            logging.error(f"Error retrieving relevant documents: {e}")
            return "Error occurred while retrieving documents."

    def add_document(self, document_path: str) -> None:
        """
        Processes and adds a document from the given path to the vector store for future retrieval tasks.

        Parameters:
            document_path (str): The file path of the document to be processed and added.
        """
        self.running = True
        try:
            self.documents_paths.append(document_path)
            loader = TextLoader(document_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
            splits = text_splitter.split_documents(docs)
            logging.info(f"Loading document from path: {document_path}")

            if self.vectorstore is None:
                self.vectorstore = Chroma.from_documents(documents=splits, embedding=InformationExtractor.embeddings)
            else:
                self.vectorstore.add_documents(docs)

            self.retriever = self.vectorstore.as_retriever(search_kwargs={'k': self.k})
            self.indexed.append(document_path)
            logging.info(f"Document '{document_path}' successfully uploaded and indexed.")
        except Exception as e:
            logging.error(f"Error adding document '{document_path}': {e}")
        finally:
            self.running = False
