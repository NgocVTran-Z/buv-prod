from datetime import datetime
import json
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utilize.const import *
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("../application/.env"))

# from model.chat import azure_openai
from backend.utils import azure_openai
# from model.embeddings import text_embedding_3large
# from backend.utils import embeddings_3_large
from backend.utils import text_embedding_3large
from utilize.connect_db import *
from utilize.queries import *


def convert_datetime(state_date, state_time):
    print("convert datetime here")
    datetime_user_input = state_date + " " + state_time

    answer_prompt = PromptTemplate.from_template(
        f"""You are an assistant bot. Your main task is to convert user input of date and time
        expressed in natural language into datetime format.

        Today is {datetime_full} \n
        and the user input is: {datetime_user_input}
        Convert the user input to the format YYYY-MM-DD hh:mm \n

        Your response should only contain answer format "YYYY-MM-DD hh:mm" and nothing else.
        """ #.format(datetime_full, datetime_user_input)
    )
    # print(answer_prompt)
    chain = answer_prompt | azure_openai | StrOutputParser()


    answer = chain.invoke({
        "datetime_user_input": datetime_user_input,
        "answer_prompt": answer_prompt
    })

    # answer = "23:59:59"

    print("sql answer:", answer)
    return answer
