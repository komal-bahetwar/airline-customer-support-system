import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# LLM Initialization
# Using Groq-supported OpenAI model
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# OpenAI Embedding model initialization
openai_embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=os.getenv('OPENAI_API_KEY'))

# Table schema for SQL agent
table_schema = """
id BIGINT, flight_no TEXT, airline_code TEXT, airline_name TEXT, origin TEXT, destination TEXT, departure_date TEXT (YYYY-MM-DD), departure_time TIME, arrival_date TEXT (YYYY-MM-DD), arrival_time TIME, status TEXT, delay_minutes INTEGER, delay_reason TEXT, terminal TEXT, gate TEXT, aircraft_type TEXT, seats_total INTEGER, seats_booked INTEGER, fare_inr INTEGER
"""
