# from examples_FewShotPrompt import examples, example_prompt
import sqlite3
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
# from models.llm_model import llm_AzureChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent, create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv

# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://dalle3-swo.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = "e51119f8d8774069a6594d92ccf7a70d"

load_dotenv(find_dotenv("../application/.env"))
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# LLM
llm = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt-35-turbo",
    temperature=0
)
smart_llm = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt-4",
    temperature=0
)
gpt_35_turbo_instruct = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt-35-turbo-instruct",
    temperature=0
)
# Embedding
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-ada-002",
    openai_api_version="2024-02-15-preview",
)


# define example for FewShotPromptTemplate
examples = [

    {
        "input": "what is the bus schedules of Monday from Tay Ho?",
        "sql_query": "select departure_time, arrival_time "
                 "from bus_trips a join bus_timetable b "
                 "on a.trip_id = b.trip_id "
                 "where b.day_of_week = 'Monday' and a.departure_district = 'Tay Ho';"
    },
    {
        # test - wrong SQL query
        # "input": "is there any bus from hai ba trung to buv campus?",
        "input": "is there any bus from hai ba trung to buv campus?",
        "sql_query": "select departure_time, arrival_time "
                 "from bus_trips a join bus_timetable b "
                 "on a.trip_id = b.trip_id "
                 "and a.arrival = 'BUV Campus' "
                 "where b.day_of_week = 'Monday' and a.departure_district = 'Hai Ba Trung';"
    },

]

# define template
example_prompt = PromptTemplate(
    input_variables=["input", "sql_query"],
    template="Q: {input}\n"
             "SQL Query (A): {sql_query}\n"
)
# print(example_prompt.format(**examples[0]))

# question = "what is the bus schedules of Monday from Cau Giay"
# question = "what is the bus schedules of Tue from hai ba trung"


# connect DB
bus_database2 = "./data/buv_sio.db"
db = SQLDatabase.from_uri(f"sqlite:///{bus_database2}")
# db = SQLDatabase.from_uri("sqlite:///bus_database2.db")
# initial llm


def get_answer(question):
    # define FewShotPromptTemplate
    few_shot_template = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="",
        suffix="Question: {input}",
        input_variables=["input"]
    )
    # print(few_shot_template.format(input=question))

    # chain - sql as output
    query = ((few_shot_template
             | llm)
             | StrOutputParser())

    def fetch_schedule_info(query):
        # Kết nối với cơ sở dữ liệu SQLite
        # conn = sqlite3.connect('bus_database2.db')
        conn = sqlite3.connect('./data/buv_sio.db')
        # create cursor
        cursor = conn.cursor()
        # run query
        cursor.execute(query)

        # get result
        results = cursor.fetchall()
        return results

    try:
        query_ = str(query.invoke(input=question).split(
            "SQL Query (A): ")[1].strip())
        result_ = fetch_schedule_info(query=query_)
    except:
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)
        result_ = write_query | execute_query

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
        
        Your answer must strictly follow this rules:
        Rule 1: your answer must provide information as nature language, not as a table or dataframe, 
        list down as different bullets to make your answer readable
        Rule 2: just answer the result of query as nature language, dont say anything about the SQL query
        Rule 3: don't mention anything about code, dataframe or data source, SQL query, technical problem
    
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )

    chain = answer_prompt | llm | StrOutputParser()

    try:
        answer = chain.invoke({
            "question": question,
            "query": query_,
            "result": result_
        })
    except:
        answer = "no answer found"
    return answer


# print(get_answer(question=question))

# db = SQLDatabase.from_uri("sqlite:///bus_database2.db")


# # ===== convert question to SQL query ============
# # llm = llm_AzureChatOpenAI(temperature=0.5)
# # question = "what is the bus schedules of 27 May from Hai Ba Trung"

# # ====== execute SQL query==========
# execute_query = QuerySQLDataBaseTool(db=db, verbose=True)
# write_query = create_sql_query_chain(llm, db)

# # ======== answer the question ======
# answer_prompt = PromptTemplate.from_template(
#     """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

#     Question: {question}
#     SQL Query: {query}
#     SQL Result: {result}
#     Answer: """
# )

# chain = (
#     RunnablePassthrough.assign(query=write_query).assign(
#         result=itemgetter("query") | execute_query
#     )
#     | answer_prompt
#     | llm
#     | StrOutputParser()
# )

# chain.invoke({"question": question})
# print(chain.invoke({"question": question}))
