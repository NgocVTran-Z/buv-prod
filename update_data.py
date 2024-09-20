
# from model.embeddings import text_embedding_3large
from backend.utils import text_embedding_3large
import os
from langchain.vectorstores.pgvector import PGVector
from langchain.indexes import SQLRecordManager, index
from langchain_core.documents.base import Document
import pandas as pd

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("./application/.env"))


host = os.getenv("PG_VECTOR_HOST")
user = os.getenv("PG_VECTOR_USER")
password = os.getenv("PG_VECTOR_PASSWORD")
database = os.getenv("PGDATABASE")
pgport = os.getenv("PGPORT")

COLLECTION_NAME = "buv_general_info"

# CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
# CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:5432/{database}"
CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{pgport}/{database}"


#---------- read data -------------
# filepath = "./data/Bus_schedules_general_info.csv"
filepath = "data/csv/old_csv/general_info.csv"
df = pd.read_csv(filepath)
data = [
    Document(page_content=row['question'], metadata={'answer': row['answer']})
    for index, row in df.iterrows()
]


#----------- embedding --------------
vector_store = PGVector(
    embedding_function=text_embedding_3large,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
)

#--------------- upload / insert -----------------
namespace = f"pgvector/{COLLECTION_NAME}"
record_manager = SQLRecordManager(
    namespace, db_url=CONNECTION_STRING
)
record_manager.create_schema()
index(
    data,
    record_manager,
    vector_store,
    cleanup="full",
    source_id_key="answer",
)







