from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.retrievers import MultiVectorRetriever
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage import InMemoryStore, LocalFileStore
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import sys
from operator import itemgetter
from typing import List
from langchain.docstore.document import Document
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
from langchain_community.vectorstores import PGVector
from sqlalchemy import create_engine, Column, Integer, Text, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv, find_dotenv
# __import__('pysqlite3')
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
load_dotenv(find_dotenv("../application/.env"))

# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://alldemo-openai.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = "5d0c9b16e7e14333918d2b4e61b36216"

AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')





# LLM
# gpt_35_turbo_16k = AzureChatOpenAI(
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="gpt-35-turbo-16k",
#     temperature=0
# )
# azure_openai = AzureChatOpenAI(
#     # openai_api_version="2023-05-15",
#     openai_api_version="2024-05-01-preview",

#     # azure_deployment="apac-gpt-35-turbo",
#     azure_deployment="demo-gpt-35-turbo-16k",
#     temperature=0
# )
# gpt_4o = AzureChatOpenAI(
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="gpt-4o",
#     temperature=0
# )
# Embedding
# embeddings = AzureOpenAIEmbeddings(
#     azure_deployment="text-embedding-ada-002",
#     openai_api_version="2024-02-15-preview",
# )

# embeddings_3_large = AzureOpenAIEmbeddings(
#     azure_deployment="text-embedding-3-large",
#     openai_api_version="2024-02-15-preview",
# )

# text_embedding_3large = AzureOpenAIEmbeddings(
#     # model="apac-text-embedding-3-large",
#     model="demo-text-embedding-3-large",

#     openai_api_version="2022-12-01",
#     openai_api_key=AZURE_OPENAI_API_KEY,
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
# )

# -----------Production-----------
azure_openai = AzureChatOpenAI(
    # openai_api_version="2023-05-15",
    openai_api_version="2024-05-01-preview",
    azure_deployment="Chat_Models",
    temperature=0
)

# azure_openai = AzureChatOpenAI(
#     # openai_api_version="2023-05-15",
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="Chat_Models_4o_mini",
#     temperature=0
# )

# azure_openai = AzureChatOpenAI(
#     # openai_api_version="2023-05-15",
#     openai_api_version="2024-02-15-preview",
#     azure_deployment="Chat_Models_4o",
#     temperature=0
# )

text_embedding_3large = AzureOpenAIEmbeddings(
    model="Embedding_Models",
    openai_api_version="2022-12-01",
    openai_api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
# database = os.getenv("PGDATABASE3")
database = os.getenv("PGDATABASE4")
# database = os.getenv("PGDATABASE2")
pgport = os.getenv("PGPORT")
COLLECTION_NAME = "langchain_collection"
# CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
# CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:5432/{database}"
CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{pgport}/{database}"
vector_store = PGVector(
embedding_function=text_embedding_3large,
collection_name=COLLECTION_NAME,
connection_string=CONNECTION_STRING,
)
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 1,
        "score_threshold": 0.8
    }
)

# Create a base class using declarative_base
Base = declarative_base()

# Define your table as a model class
class FAQ(Base):
    __tablename__ = 'question_answer'  # Table name in the database

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    question = Column(Text, nullable=False)  # Question column of type text
    answer = Column(Text, nullable=False)  # Answer column of type text
    bot_type = Column(Text, nullable=False)  # Bot type column of type text

# --------------------------------

# language_detection_prompt_template = """
# Given the user question below, detect the language of it as either `Vietnamese`, or `Other`.

# Do not respond with more than one word.

# <question>
# {input}
# </question>

# Language:"""
language_detection_prompt_template = """
Identify the language of the text below as either `Vietnamese` or `Other`.

Respond with only one word.

<text>
{input}
</text>

Language:"""

# language_detection_chain = (
#     PromptTemplate.from_template(language_detection_prompt_template)
#     | gpt_4o
#     | StrOutputParser()
# )
language_detection_chain = (
    PromptTemplate.from_template(language_detection_prompt_template)
    | azure_openai
    | StrOutputParser()
)
