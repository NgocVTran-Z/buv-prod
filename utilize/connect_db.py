# from langchain.chat_models import ChatOpenAI
# from langchain.chains import create_tagging_chain, create_tagging_chain_pydantic
# from langchain.prompts import ChatPromptTemplate
#
# from enum import Enum
# from pydantic import BaseModel, Field
# from langchain_openai import AzureChatOpenAI
# from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
#
# from typing import List
#
# from langchain.output_parsers import PydanticOutputParser
# from langchain_core.prompts import PromptTemplate
# from langchain_core.pydantic_v1 import BaseModel, Field, validator
# from langchain_openai import ChatOpenAI
#
# from langchain_core.utils.function_calling import convert_to_openai_function
#
# from datetime import datetime
# import json
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("../application/.env"))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text
import pandas as pd

# from model.chat import azure_openai
# from model.embeddings import text_embedding_3large
#
# from langchain_core.output_parsers import StrOutputParser
# from utilize.queries import *
import sqlite3

def fetch_schedule_info(state, query):
    # Connect to the SQLite database
    conn = sqlite3.connect('./data/bus_database.db')
    cursor = conn.cursor()

    # Query to fetch all table names
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all table names
    # tables = cursor.fetchall()
    # print(tables)

    # def fetch_schedule_info():
        # run query

    # query = query_full_info()
    # print("den duoc day")
    cursor.execute(query)

    # get result
    results_query = cursor.fetchall()
    # print(results_query)
    return results_query
# print(results)
# return results

def fetch_schedule_info_postgres(state, query):
    # connect to postgresql
    db_username = os.getenv("PG_VECTOR_USER")
    db_password = os.getenv("PG_VECTOR_PASSWORD")
    db_host = os.getenv("PG_VECTOR_HOST")
    # db_port = 5432
    db_port = int(os.getenv("PGPORT"))
    db_name = os.getenv("PGDATABASE2")
    # db_name = os.getenv("PGDATABASE3")
    # db_name = os.getenv("PGDATABASE5")

    # engine = create_engine(f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')
    engine = create_engine(f'postgresql+psycopg://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

    bus_trips_df = pd.read_sql(query, engine)
    bus_trips_df = bus_trips_df[["stop_name", "stop_time"]]

    return bus_trips_df