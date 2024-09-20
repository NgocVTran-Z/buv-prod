from datetime import datetime
import json
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utilize.const import *
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("../application/.env"))

# from model.chat import azure_openai
# from backend.utils import gpt_35_turbo_16k
# from model.embeddings import text_embedding_3large
# from backend.utils import text_embedding_3large
from utilize.connect_db import *
from utilize.queries import *

def convert_sql(state):

    # query = query_full_info(state)
    query = query_full_info_postgres(state)

    # print(query)
    print("+++++++++++++++++++++++++++++++++++++++++")
    # result = fetch_schedule_info(state, query)
    # print("sql result:", result)

    # result query postgres
    result = fetch_schedule_info_postgres(state, query)
    print("sql result:", result)

    # print("what is the bus schedule from " + state["pick-up point"][0] + " to " + state["drop-off point"][0] + " on " + state["specific date"] + " at " + state["specific time"] + "?")
    question = "what is the bus schedule from " + state["pick-up point"][0] \
               + " to " + state["drop-off point"][0] + " on " + state["specific date"][0] \
               + " at " + state["specific time"][0] + "?"
    # print(question)

    # answer_prompt = PromptTemplate.from_template(
    #     """You are an assistant bot specialized in answering user questions about bus schedules.
    #     Your input will be the user's question, is here: \n
    #     {question} \n
    #
    #     And the information you receive will be the result of a query corresponding to that question, here:
    #     {result}
    #
    #     Your task is to convert the query result into natural language to respond to the user
    #     in the most natural and understandable way. If the query result is empty, inform the
    #     user that there is no bus available. Absolutely do not generate incorrect
    #     information beyond the query result.
    #
    #     If the response contains multiple points, list them as bullet points for easier reading.
    #     """
    # )
    answer_prompt = PromptTemplate.from_template(
        """You are an assistant bot specialized in providing information about bus schedules.
        User's question: \n {question} \n
        Query result: \n {result} \n
        Your task is to convert the query result into a natural language response for the user. 
        If there are multiple pieces of information, list them as bullet points for clarity. 
        If the query result is empty, inform the user that there are no buses available. 
        Do not generate information that is not present in the query result.
        """
    )


    chain = answer_prompt | azure_openai | StrOutputParser()
    print(chain.invoke({
            "question": question,
            # "query": query_,
            "result": result
        }))

    try:
        answer = chain.invoke({
            "question": question,
            # "query": query_,
            "result": result
        })
    except Exception as e:
        print("sql bug:", e)
        answer = "Sorry, there is no bus found."
    # answer = answer.replace("-", "\n-")
    print("Bot answer:", answer)

    return answer




