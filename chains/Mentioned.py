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


class Mentioned(BaseModel):
    """
    An assistant, support to check a sentence is True or False
    """

    mention: bool = Field(
        enum=[True, False],
        description="Checking the input sentence is True or False"
    )

parser_mention = PydanticOutputParser(pydantic_object=Mentioned)

prompt_mention = ChatPromptTemplate.from_messages([
    ("system",
    "You are an assistant. Your job is checking the user's input if it's correct or not."
    "Wrap the output in `json` tags\n{format_instructions}"),
    # (),
    ("human", "{query}"),
]).partial(format_instructions=parser_mention.get_format_instructions())

chain_mention = prompt_mention | azure_openai

