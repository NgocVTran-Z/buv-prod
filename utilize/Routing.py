from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("../application/.env"))
import streamlit as st
from langchain_core.pydantic_v1 import BaseModel, Field, validator
# from model.chat import azure_openai
from backend.utils import azure_openai
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from utilize.generate_general_info import *
from utilize.generate_busschedule_info import *
class ContentClarifier(BaseModel):
    """
    An bot assistant, support to check a sentence is about: \n
    1. General request (for claim, complain, asking for hotline information etc.)
    2. Detail information about bus route (with route name, pickup and dropoff point, specific date time)
    """

    content_type: str = Field(
        enum=["general", "specific"],
        description="Clarify the type of input information as general"
    )

def clarify(question, chatbot_type):
    print("clarify:", chatbot_type)

    if chatbot_type=="Bus General Information":
        return general_info(question)
    if chatbot_type=="Bus Schedule":
        return bus_schedule(question)
    # def route(info):
    #     if "general" in info["topic"].dict()["content"].lower():
    #         return general_info(info["question"])
    #     elif "specific" in info["topic"].dict()["content"].lower():
    #         return bus_schedule(info["question"])
    #
    #
    # parser_contentclarify = PydanticOutputParser(pydantic_object=ContentClarifier)
    # template = """You are an assistant bot with the task of categorizing customer inquiries into one of two categories:
    # 1) general: general questions about bus schedules
    # 2) specific: detailed questions about bus schedules.
    # \n
    # Before deciding how to categorize the customer's question, always ask yourself: \n
    # "Does this question ask for detailed information about the bus schedule?" \n
    # Then, classify accordingly.
    #     """
    # prompt_contentclarify = ChatPromptTemplate.from_messages([
    #     ("system", template),
    #     ("system", "Wrap the output in `json` tags\n{format_instructions}"),
    #     # (),
    #     ("human", "User input: {question}"),
    # ]).partial(format_instructions=parser_contentclarify.get_format_instructions())
    #
    # chain_contentclarify = prompt_contentclarify | azure_openai
    #
    #
    # full_chain = ({"topic": chain_contentclarify, "question": lambda x: x["question"]}
    #               | RunnableLambda(route)
    #               )
    # context = st.session_state.latest_bot_answer + " " + question
    # result = full_chain.invoke({"question": context})
    #
    # return result


#------------ routing function -----------------------
def general_info(question:str):
    # print("try get general info")
    try:
        answer, suggested_questions, url_ = get_prompt_ans(question)
    except Exception as e:
        print(e)
        answer = "Sorry, I dont' find any relevant information ..."
        suggested_questions = []
        url_ = {
            "Zalo QR Code": [],
            "Bus images": [],
            # "Bus Introduction"
            "GPS Link": []
        }
    # answer = question + " GENERAL INFOR answer 1"
    # answer = " GENERAL INFOR"
    # suggested_questions = ["GENERAL INFOR", "suggest 2"]
    return answer, suggested_questions, url_


def bus_schedule(question):
    # print(question)
    answer, suggested_questions = get_busschedule_ans(question)
    # print(answer)
    url_ = {
        "Zalo QR Code": [],
        "Bus images": [],
        "GPS Link": []
    }
    # answer = "BUS SCHEDULE"
    # suggested_questions = ["BUS SCHEDULE", "suggest 2"]
    return answer, suggested_questions, url_


