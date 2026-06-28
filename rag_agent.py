import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec, PineconeApiException
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

from llm_config import llm, openai_embedding_model

load_dotenv()

# Pinecone details from environment variables
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "airline-faq-index")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

# Path to the PDF document
PDF_PATH = "data/Knowledge_Base_for_Airline_Info_and_FAQs.pdf"

# Load PDF document
loader = PyMuPDFLoader(PDF_PATH)
docs = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    add_start_index=True,
)
chunks = text_splitter.split_documents(docs)

# Initialize Pinecone client and create/connect to index
pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
try:
    if PINECONE_INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(
            PINECONE_INDEX_NAME,
            dimension=openai_embedding_model.dimensions, # Assuming openai_embedding_model has a dimensions attribute
            metric='cosine',
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
        )
        print(f"Pinecone index '{PINECONE_INDEX_NAME}' created.")
    else:
        print(f"Pinecone index '{PINECONE_INDEX_NAME}' already exists.")
except PineconeApiException as e:
    if "ALREADY_EXISTS" in str(e):
        print(f"Pinecone index '{PINECONE_INDEX_NAME}' already exists. Skipping creation.")
    else:
        print(f"An error occurred while creating the Pinecone index: {e}")

# Initialize Vector store from existing index or create new one
vectorstore = PineconeVectorStore.from_documents(
    chunks,
    openai_embedding_model,
    index_name=PINECONE_INDEX_NAME
) if PINECONE_INDEX_NAME not in pinecone.list_indexes() else PineconeVectorStore.from_existing_index(
    index_name=PINECONE_INDEX_NAME,
    embedding=openai_embedding_model
)

print(f"Pinecone vector store initialized from index: {PINECONE_INDEX_NAME}")

# Define RAG chain
retriever = vectorstore.as_retriever()

rag_prompt_template = PromptTemplate.from_template(
    """You are an airline customer support agent. Use the following pieces of context to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context: {context}
    Question: {question}
    Answer:"""
)

rag_chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question")
    }
    | rag_prompt_template
    | llm
    | StrOutputParser()
)
