from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field, validator

from utilize.const import *
# from model.chat import azure_openai
from backend.utils import azure_openai

from langchain_core.prompts import PromptTemplate

import json
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI
import os


class BusSchedule(BaseModel):
    """
    A bus schedule between Hanoi and BUV Campus, includes:

    1. Route name (route_name): Name of the bus route.
    2. Pickup point (pickup_point): The location where the user wants to catch the bus, the starting point mentioned by the user.
    3. Drop-off point (dropoff_point): The destination where the user wants to go.
    4. Date and time: The specific time when the user wants information about the bus route.
    """

    route_name: List[str] = Field(
        ...,
        enum=bus_route_name,
        description="Name of bus route. This includes only the following names: Hai Ba Trung, Cau Giay, Ha Dong, Tay Ho, Ecopark.\
                    These are also district names within the city of Hanoi, but not city names.\
                    If the bus route is not mentioned by the user, leave this field blank.")

    pickup_point: List[str] = Field(
        ...,
        enum=point_name,
        description="""The values of location where user wants to catch the bus.\n
                    Check which one is appear in the user's input. If the pick-up point is not mentioned in user's query, leave this field blank.""")
    dropoff_point: List[str] = Field(
        ...,
        enum=point_name,
        description="""The values of destination where the user wants to go.\n
                    Check which one is appear in the user's input. If the drop-off point is not mentioned in user's query, leave this field blank.""")
    date_: List[str] = Field(
        ...,
        description="The specific Date when the user wants information about the bus route.\
                    If it's not clear, then note it as user's input. \
                    If the Date is not mentioned by the user, leave this field blank.")
    time_: List[str] = Field(
        ...,
        description="The specific Time (hour and minute) when the user wants information about the bus route.\
                    If it's not clear, then note it as user's input. \
                    If the Time is not mentioned by the user, leave this field blank.")


# tag the route of bus
parser_busschedule = PydanticOutputParser(pydantic_object=BusSchedule)

# Prompt
prompt_busschedule = ChatPromptTemplate.from_messages([
    ("system",
     # """
     # You are an expert extraction algorithm. Your job is to tag the text of the user's query.
     # Only extract the properties mentioned in the 'BusSchedule' function.
     # If you do not know the value of an attribute asked to extract, return null for the attribute's value.\n
     # {format_instructions}
     # """),
    """You are an expert extraction algorithm. Your job is tag the text of user's query.\n
    User will ask about bus schedule, and inside user's query, there will be information about the bus schedule that they want to ask, include: route name, pick-up point, drop-off point, time and date.\n
    You are not answer the question, you only extract the properties defined in the 'BusSchedule' function, from user's query. \n
    If you can not find those information in user's query, leave it blank. \n
    
    If you do not know the value of an attribute asked to extract, return null for the attribute's value. \n 
    Wrap the output in tags\n{format_instructions}"""),
    # (),
    ("human", "{query}"),
]).partial(format_instructions=parser_busschedule.get_format_instructions())

chain_busschedule = prompt_busschedule | azure_openai

# test_quest = "Can you please provide the name or location of the pick-up point for your desired bus route? BUV Campus"
# msg = chain_busschedule.invoke({"query": test_quest})
# print(msg)
# # msg_json = convert_to_json(msg.dict())